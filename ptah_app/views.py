from zope import interface
from memphis import view, form, config
from pyramid.httpexceptions import HTTPFound

import ptah
import ptah_cms
from ptah.security import authService
from ptah_cms import tinfo, interfaces


view.registerLayout(
    'page', view.INavigationRoot,
    template = view.template("ptah_app:templates/layoutpage.pt"))


class LayoutWorkspace(view.Layout):
    view.layout('workspace', view.INavigationRoot, parent="page")

    template=view.template("ptah_app:templates/layoutworkspace.pt")

    def update(self):
        self.root = getattr(self.request, 'root', None)
        self.user = ptah.authService.getCurrentPrincipal()
        self.isAnon = self.user is None


class ContentLayout(view.Layout):
    view.layout('', interfaces.IContent, parent="workspace",
                template=view.template("ptah_app:templates/layoutcontent.pt"))

    def update(self):
        context = self.context
        sm = self.request.registry
        ti = self.context.__type__

        actions = []
        for action in ti.actions:
            if action.permission:
                if authService.checkPermission(context, action.permission):
                    actions.append(action)
            else:
                actions.append(action)

        for name, action in sm.getAdapters((context,), interfaces.IAction):
            if action.permission:
                if authService.checkPermission(context, action.permission):
                    actions.append(action)
            else:
                actions.append(action)

        self.actions = actions


view.registerLayout(
    '', context=view.INavigationRoot, parent='workspace',
    template = view.template("ptah_app:templates/layoutdefault.pt"))


class ContainerListing(view.View):
    view.pyramidView(
        'index.html', interfaces.IContainer, default=True,
        template=view.template("ptah_app:templates/folder_listing.pt"))

    def update(self):
        if 'form.buttons.remove' in self.request.POST:
            uuids = self.request.POST.getall('item')
            print '=============', uuids

        if 'form.buttons.rename' in self.request.POST:
            uuids = self.request.POST.getall('item')
            print '=============', uuids

        if 'form.buttons.cut' in self.request.POST:
            uuids = self.request.POST.getall('item')
            print '=============', uuids


#class RenameForm(view.View):
#    view.pyramidView(
#        'rename.html', interfaces.IContainer,
#        template=view.template("tartaroo:templates/folder_rename.pt"))
    
    


class Adding(view.View):
    view.pyramidView(
        '+', interfaces.IContainer,
        template=view.template("ptah_app:templates/adding.pt"))
    
    def update(self):
        self.url = self.request.resource_url(self.context)

        self.types = types = []
        for ti in tinfo.registered.values():
            if ti.add is not None:
                types.append(ti)


sharingAction = ptah_cms.Action(**{'id': 'adding',
                                   'title': 'Add content',
                                   'action': '+/',
                                   'permission': ptah.View})

@config.adapter(ptah_cms.IContainer, name='adding')
@interface.implementer(ptah_cms.IAction)
def addingActionAdapter(context):
    return sharingAction
