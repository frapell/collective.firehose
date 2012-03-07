from zope.interface import implements
from zope.interface import alsoProvides

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from zope.site.hooks import getSite

from zope.formlib import form
from zope.schema.vocabulary import SimpleVocabulary

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.registry.interfaces import IRegistry
from zope.schema.interfaces import IContextSourceBinder
from AccessControl.interfaces import IRoleManager

from zope.security import checkPermission
from zExceptions import NotFound

from collective.firehose import _

from itertools import chain

import time
import redis

def PortalTypes(context):
    portal_types = getToolByName(context, "portal_types")
    site_properties = getToolByName(context, "portal_properties").site_properties

    not_searched = site_properties.getProperty('types_not_searched', [])

    portal_types = getToolByName(context, "portal_types")
    types = portal_types.listContentTypes()

    # Get list of content type ids which are not filtered out
    prepared_types = [t for t in types if t not in not_searched]

    return SimpleVocabulary.fromValues(prepared_types)


alsoProvides(PortalTypes, IContextSourceBinder)


class IMostVisitedContentPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    header = schema.TextLine(title=_(u'Header'),
                             description=_(u"The header for the portlet. Leave empty for none."),
                             required=False)

    types = schema.List(title=_(u"Content types to check"),
                        description=_(u"Choose which content types should be shown in the portlet"),
                        required=True,
                        value_type=schema.Choice(source=PortalTypes))

    max_results =  schema.Int(title=_(u'Maximum results'),
                               description=_(u"The maximum results number."),
                               required=True,
                               default=10)

    hours = schema.Int(title=_(u'Hours'),
                       description=_(u"How many hours ago."),
                       required=True,
                       default=1)


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IMostVisitedContentPortlet)

    header = u""
    types = []
    max_results = 10
    hours = 1

    def __init__(self,
                 types,
                 header=u"",
                 max_results=10,
                 hours=1):

        self.header = header
        self.types = types
        self.max_results = max_results
        self.hours = hours

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return _(u"Most visited content")



class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('most_visited.pt')


    def getHeader(self):
        """
        Returns the header for the portlet
        """
        return self.data.header

    def canEdit(self):
        return checkPermission('cmf.ModifyPortalContent', self.context)

    def getMostVisitedContent(self):
        site = getSite()
        site_url = site.absolute_url()
        r = redis.StrictRedis(host='localhost', port=6379, db=0)

        pipe = r.pipeline()

        timeslot = time.time() // 3600

        for hour in range(self.data.hours + 1):
            # We need to get all results, so we can filter out
            amount = r.zcard('tophits.%s' % (timeslot-hour))
            pipe.zrevrange('tophits.%s' % (timeslot-hour), 0, amount, withscores=True, score_cast_func=int)

        redis_results = pipe.execute()
        partial_results = {}
        for hour_result in redis_results:
            for result in hour_result:
                if result[0].endswith('.css') or\
                   result[0].endswith('.kss') or\
                   result[0].endswith('.gif') or\
                   result[0].endswith('.js'):
                    # We have a resource, just ignore it
                    continue

                count = partial_results.get(result[0], 0)
                count += result[1]
                partial_results[result[0]] = count

        # Filter out resources
        results = []
        for i in partial_results:
            if len(results) == self.data.max_results:
                # If we already have all results we need, then get out of loop
                break

            # We have a candidate, get the relative path
            rel_path = i[len(site_url)+1:]
            # Now let's get the proper object
            try:
                obj = site.restrictedTraverse(rel_path)
            except AttributeError:
                # Invalid resource. Ignore
                continue
            except KeyError:
                # Invalid resource. Ignore
                continue
            except NotFound:
                # Resource not found. Ignore
                continue
            except TypeError:
                # Invalid resource. Ignore
                continue
            except IndexError:
                # Invalid resource. Ignore
                continue

            # Let's check, we actually have a CT
            # XXX: Not sure which interface to use here. It should be common
            #      to AT and Dexterity types
            if not IRoleManager.providedBy(obj):
                continue

            # Finally, let's check that this object is of the type we
            # want
            if obj.portal_type in self.data.types:
                # Yeah ! append it to the results
                # XXX: Shall we store the hit number ? we will for now...
                results.append((obj, partial_results[i]))

        # Now, sort it using the number of hits
        results.sort(key=lambda x:x[1], reverse=True)

        return results


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IMostVisitedContentPortlet)

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IMostVisitedContentPortlet)
