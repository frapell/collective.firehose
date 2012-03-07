from Products.CMFCore.utils import getToolByName

def install(portal, reinstall=False):
    setup_tool = getToolByName(portal, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile('profile-collective.firehose:default')
    return "Ran all install steps."

def uninstall(portal, reinstall=False):
    if not reinstall:
        setup_tool = getToolByName(portal, 'portal_setup')
        setup_tool.runAllImportStepsFromProfile('profile-collective.firehose:uninstall')
        return "Ran all uninstall steps."