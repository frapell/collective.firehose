
from zope.component import getUtility

from plone.registry.interfaces import IRegistry

from Products.Five.browser import BrowserView

from collective.firehose.controlpanel import IFirehoseSettings


class Conditions(BrowserView):

    def store_hits(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IFirehoseSettings)

        return settings.store_hits

    def store_visit_time(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IFirehoseSettings)

        return settings.store_visit_time
