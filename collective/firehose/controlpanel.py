# -*- coding: utf-8 -*-

from zope import schema

from zope.interface import Interface

from plone.app.registry.browser import controlpanel

from collective.firehose import _


class IFirehoseSettings(Interface):
    """ 
    Interface for the control panel form.
    """

    store_hits = schema.Bool(
        title=_(u'Store every page hit'),
        description=_(u"If checked, url, visitor's IP, userid (in case of authenticated) and timestamp will be stored on every page hit."),
        default=True
        )

    store_visit_time = schema.Bool(
        title=_(u'Store time on page'),
        description=_(u"If checked, the time spent on each url will be stored, along the userid and visitor's IP."),
        default=True
        )


class FirehoseSettingsEditForm(controlpanel.RegistryEditForm):
    schema = IFirehoseSettings
    label = _(u"Firehose Settings")
    description = _(u"Here you can modify the settings for collective.firehose.")


class FirehoseSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = FirehoseSettingsEditForm
