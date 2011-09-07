from memphis import view
from zope import interface
from pyramid import security
from webob.exc import HTTPForbidden

from ptah.settings import PTAH
from ptah.interfaces import IAuthentication, IPtahManageRoute, IPtahModule


view.pageletType('ptah-module-actions', IPtahModule)


class PtahModule(object):
    interface.implements(IPtahModule)

    name = ''
    title = ''
    description = ''

    def url(self, request):
        return '%s/'%self.name

    def bind(self, manager, request):
        clone = self.__class__.__new__(self.__class__)
        clone.__dict__.update(self.__dict__)
        clone.__name__ = self.name
        clone.__parent__ = manager
        clone.request = request
        return clone

    def available(self, request):
        return True


def PtahAccessManager(id):
    """ default access manager """
    if id and id in PTAH.managers:
        return True

    return False


ACCESS_MANAGER = PtahAccessManager

def setAccessManager(func):
    global ACCESS_MANAGER
    ACCESS_MANAGER = func


class PtahManageRoute(object):
    interface.implements(IPtahManageRoute)

    __name__ = 'ptah-manage'
    __parent__ = view.DefaultRoot()

    def __init__(self, request):
        self.request = request
        self.registry = request.registry

        userid = security.authenticated_userid(request)
        if not ACCESS_MANAGER(userid):
            raise HTTPForbidden()

    def __getitem__(self, key):
        mod = self.registry.queryUtility(IPtahModule, key)

        if mod is not None:
            return mod.bind(self, self.request)

        raise KeyError(key)


view.registerRoute(
    'ptah-manage','/ptah-manage/*traverse',
    PtahManageRoute, use_global_views=True)

view.static('ptah', 'ptah:templates/static')

view.registerLayout(
    '', IPtahManageRoute, parent='page',
    template=view.template("ptah:templates/ptah-layout.pt"))

view.registerPagelet(
    'ptah-module-actions',
    template = view.template('ptah:templates/moduleactions.pt'))


class LayoutPage(view.Layout):
    view.layout('page', IPtahManageRoute,
                template=view.template("ptah:templates/ptah-page.pt"))

    def update(self):
        request = self.request
        registry = request.registry

        self.username = security.authenticated_userid(request)
        #self.user = registry.getUtility(IAuthentication).getCurrentUser()

        mod = self.viewcontext
        while not IPtahModule.providedBy(mod):
            mod = getattr(mod, '__parent__', None)
            if mod is None:
                break

        self.module = mod


class ManageView(view.View):
    """List ptah modules"""
    view.pyramidView(
        'index.html', IPtahManageRoute,
        route = 'ptah-manage', default=True, layout='page',
        template = view.template('ptah:templates/manage.pt'))

    __intr_path__ = '/ptah-manage/index.html'

    def update(self):
        reg = self.request.registry

        mods = []
        for name, mod in reg.getUtilitiesFor(IPtahModule):
            mods.append((mod.title, mod))

        mods.sort()
        self.modules = [mod for _t, mod in mods]
