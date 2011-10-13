from zope import interface
from memphis import view, form, config
from pyramid.httpexceptions import HTTPFound, HTTPNotFound

import ptah
import ptah_cms
from ptah import authService, manage
from ptah_cms import tinfo, interfaces, events

from forms import AddForm
from uiactions import listUIActions


view.registerLayout(
    'page', ptah_cms.ApplicationRoot,
    template = view.template("ptah_app:templates/layoutpage.pt"))

view.registerLayout(
    'ptah-security', ptah_cms.ApplicationRoot, parent='workspace',
    template = view.template("ptah_app:templates/layout-ptahsecurity.pt"))


class LayoutWorkspace(view.Layout):
    view.layout('workspace', ptah_cms.ApplicationRoot, parent="page",
                template=view.template("ptah_app:templates/layoutworkspace.pt"))

    def update(self):
        self.root = getattr(self.request, 'root', None)
        self.user = authService.get_current_principal()
        self.isAnon = self.user is None
        self.ptahManager = manage.ACCESS_MANAGER(authService.getUserId())


class ContentLayout(view.Layout):
    view.layout('', interfaces.IContent, parent="workspace",
                template=view.template("ptah_app:templates/layoutcontent.pt"))

    def update(self):
        self.actions = listUIActions(self.context, self.request)


def defaultView(renderer):
    def wrap(context, request):
        if context.view:
            item = ptah_cms.load(context.view)
            if item is None:
                return renderer(context, request)

            request.context = item
            return view.renderView('', item, request)

        view = renderer(context, request)
        view.update()
        return view.render()
    return wrap


listing_template = view.template("ptah_app:templates/listing.pt")

class ContainerListing(view.View):
    view.pyramidView('listing.html', interfaces.IContainer,
                     template = listing_template)

    def update(self):
        context = self.context
        request = self.request
        registry = request.registry

        self.deleteContent = ptah.checkPermission(
            ptah_cms.DeleteContent, context)

        # cms(uri).read()
        # cms(uri).create(type)
        # cms(uri).delete()
        # cms(uri).update(**kwargs)
        # cms(uri).items(offset, limit)

        if self.deleteContent and 'form.buttons.remove' in request.POST:
            uris = self.request.POST.getall('item')
            for uri in uris:
                ptah_cms.cms(uri).delete()

                self.message("Selected content items have been removed.")

        if 'form.buttons.rename' in request.POST:
            uris = self.request.POST.getall('item')
            print '=============', uris

        if 'form.buttons.cut' in request.POST:
            uris = self.request.POST.getall('item')
            print '=============', uris


#@defaultView

class ViewContainer(ContainerListing):
    view.pyramidView(context = interfaces.IContainer,
                     template = listing_template)


class RenameForm(view.View):
    view.pyramidView(
        'rename.html', interfaces.IContainer,
        template=view.template("ptah_app:templates/folder_rename.pt"))


class Adding(view.View):
    view.pyramidView('+', interfaces.IContainer)

    template=view.template("ptah_app:templates/adding.pt")

    def update(self):
        self.url = self.request.resource_url(self.context)

        types = [(t.title, t) for t in
                 self.context.__type__.listTypes(self.context)]
        types.sort()

        self.types = [t for _t, t in types]

    def render(self):
        subpath = self.request.subpath
        if subpath and subpath[0]:
            tname = subpath[0]
            tinfo = ptah_cms.Types.get('cms+type:%s'%tname)
            if tinfo is None:
                raise HTTPNotFound

            form = AddContentForm(tinfo, self, self.request)
            form.update()
            return form.render()

        return super(Adding, self).render()


class AddContentForm(AddForm):

    def __init__(self, tinfo, form, request):
        super(AddContentForm, self).__init__(form, request)

        self.tinfo = tinfo
        self.container = form.context


class DefaultContentView(form.DisplayForm):
    view.pyramidView(
        context = ptah_cms.IContent,
        permission = ptah_cms.View,
        template=view.template("ptah_app:templates/contentview.pt"))

    @property
    def fields(self):
        return self.context.__type__.fieldset

    def getContent(self):
        data = {}
        for name, field in self.context.__type__.fieldset.items():
            data[name] = getattr(self.context, name, field.default)

        return data
