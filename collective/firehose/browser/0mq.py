
import json
import zmq

from datetime import datetime

from zope.site.hooks import getSite

from plone.uuid.interfaces import IUUID

from Products.CMFCore.utils import getToolByName

from Products.Five.browser import BrowserView


zmq_context = zmq.Context()
zmq_pub = zmq_context.socket(zmq.PUB)
zmq_pub.connect("ipc:///tmp/collective.firehose.sock")


class Hit(BrowserView):

    def __call__(self):
        pm = getToolByName(self.context, 'portal_membership')
        if not pm.isAnonymousUser():
            auth_member = pm.getAuthenticatedMember()
            userid = auth_member.getMemberId()
        else:
            userid = 'anonymous'

        visitor_ip = self.request.REMOTE_ADDR

        date = datetime.now()

        try:
            uuid = IUUID(self.context)
        except TypeError:
            uuid = 0

        url = self.request.URL1

        portal = getSite()
        portal_path = portal.getPhysicalPath()

        try:
            path = self.context.getPhysicalPath()
            path = path[len(portal_path):]
        except:
            path = tuple()

        msg = {'msg_type': 'hit',
               'date': date.strftime("%Y-%m-%d"),
               'time': date.strftime("%H:%M:%S"),
               'visitor_ip': visitor_ip,
               'userid': userid,
               'uuid': uuid,
               'url': url,
               'path': path }

        zmq_pub.send(json.dumps(msg))

        return


class VisitTime(BrowserView):

    def __call__(self, visited_time):
        pm = getToolByName(self.context, 'portal_membership')
        if not pm.isAnonymousUser():
            auth_member = pm.getAuthenticatedMember()
            userid = auth_member.getMemberId()
        else:
            userid = 'anonymous'

        visitor_ip = self.request.REMOTE_ADDR

        date = datetime.now()

        try:
            uuid = IUUID(self.context)
        except TypeError:
            uuid = 0

        url = self.request.URL1

        portal = getSite()
        portal_path = portal.getPhysicalPath()
        
        try:
            path = self.context.getPhysicalPath()
            path = path[len(portal_path):]
        except:
            path = tuple()

        msg = {'msg_type': 'visit_time',
               'date': date.strftime("%Y-%m-%d"),
               'time': date.strftime("%H:%M:%S"),
               'visitor_ip': visitor_ip,
               'userid': userid,
               'uuid': uuid,
               'url': url,
               'path': path,
               'visited_time': visited_time }

        zmq_pub.send(json.dumps(msg))

        return