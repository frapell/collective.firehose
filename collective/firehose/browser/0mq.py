
import zmq

from datetime import datetime

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

        zmq_pub.send('hit %s %s %s %s %s' % (date,
                                             visitor_ip,
                                             userid,
                                             uuid,
                                             url))

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

        zmq_pub.send('visit_time %s %s %s %s %s %s' % (date,
                                                       visitor_ip,
                                                       userid,
                                                       uuid,
                                                       url,
                                                       visited_time))

        return