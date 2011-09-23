from zope import interface
from memphis import view, form, config
from pyramid.httpexceptions import HTTPFound

import ptah
import ptah_cms
from ptah import authService
from ptah_cms import tinfo, interfaces, events

from interfaces import IPtahAppRoot


view.registerLayout(
    'page', IPtahAppRoot,
    template = view.template("ptah_app:templates/layoutpage.pt"))


class LayoutWorkspace(view.Layout):
    view.layout('workspace', IPtahAppRoot, parent="page")

    template=view.template("ptah_app:templates/layoutworkspace.pt")

    def update(self):
        self.root = getattr(self.request, 'root', None)
        self.user = ptah.authService.getCurrentPrincipal()
        self.isAnon = self.user is None


class ContentLayout(view.Layout):
    view.layout('', interfaces.IContent, parent="workspace",
                template=view.template("ptah_app:templates/layoutcontent.pt"))

    def update(self):
        ti = self.context.__type__
        self.actions = ti.listAction(self.context, self.request)


view.registerLayout(
    '', context=IPtahAppRoot, parent='workspace',
    template = view.template("ptah_app:templates/layoutdefault.pt"))


def defaultView(renderer):
    def wrap(context, request):
        if context.view:
            item = ptah_cms.loadContent(context.view)
            if item is None:
                return renderer(context, request)

            request.context = item
            return view.renderView('', item, request)

        return renderer(context, request)
    return wrap


listing_template = view.template("ptah_app:templates/listing.pt")

class ContainerListing(view.View):
    view.pyramidView('listing.html', interfaces.IContainer,
                     template = listing_template)

    def update(self):
        context = self.context
        request = self.request
        registry = request.registry
        
        if 'form.buttons.remove' in request.POST:
            uuids = self.request.POST.getall('item')
            for uuid in uuids:
                item = ptah_cms.loadContent(uuid)
                if item and item.__parent__ is context:
                    del context[item]

                self.message("Selected content items have been removed.")

        if 'form.buttons.rename' in request.POST:
            uuids = self.request.POST.getall('item')
            print '=============', uuids

        if 'form.buttons.cut' in request.POST:
            uuids = self.request.POST.getall('item')
            print '=============', uuids


class ViewContainer(ContainerListing):
    view.pyramidView('index.html', default=True, decorator = defaultView,
                     template = listing_template)


class RenameForm(view.View):
    view.pyramidView(
        'rename.html', interfaces.IContainer,
        template=view.template("ptah_app:templates/folder_rename.pt"))


class Adding(view.View):
    view.pyramidView(
        '+', interfaces.IContainer,
        template=view.template("ptah_app:templates/adding.pt"))

    def update(self):
        self.url = self.request.resource_url(self.context)

        types = [(t.title, t) for t in
                 self.context.__type__.listTypes(self.context)]
        types.sort()

        self.types = [t for _t, t in types]
