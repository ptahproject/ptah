from memphis import view, config
from zope import interface
from pyramid.security import authenticated_userid
from pyramid.httpexceptions import HTTPFound, HTTPForbidden

from ptah import resolve
from ptah.settings import PTAH_CONFIG
from ptah.authentication import authService


class IPtahRoute(interface.Interface):
    """ ptah route """


class IPtahManageRoute(view.INavigationRoot):
    """ user management route """


class IPtahModule(interface.Interface):
    """ module """

    name = interface.Attribute('Module name')
    title = interface.Attribute('Module title')

    def url(request):
        """ return url to this module """

    def bind(manager, request):
        """ bind module to context """

    def available(request):
        """ is module available """


MODULES = {}

class PtahModule(object):
    interface.implements(IPtahModule)

    name = ''
    title = ''

    def __init__(self, manager, request):
        self.__parent__ = manager
        self.request = request

    def url(self):
        return '%s/'%self.name

    @property
    def __name__(self):
        return self.name

    def available(self):
        return True


def manageModule(id):
    info = config.DirectiveInfo(allowed_scope=('class',))

    def _complete(cls, id):
        MODULES[id] = cls

        cls.name = id

    info.attach(
        config.ClassAction(
            _complete, (id,),
            discriminator = ('ptah:manage-module', id))
        )


INTROSPECTIONS = {}

def introspection(id):
    info = config.DirectiveInfo(allowed_scope=('class',))

    def _complete(cls, id):
        INTROSPECTIONS[id] = cls
        cls.name = id

    info.attach(
        config.ClassAction(
            _complete, (id,),
            discriminator = ('ptah:introspection', id))
        )


def PtahAccessManager(id):
    """ default access manager """
    if '*' in PTAH_CONFIG.managers:
        return True

    principal = resolve(id)

    if principal is not None and principal.login in PTAH_CONFIG.managers:
        return True

    return False


ACCESS_MANAGER = PtahAccessManager

def setAccessManager(func):
    global ACCESS_MANAGER
    ACCESS_MANAGER = func


class DefaultRoot(object):
    interface.implements(view.INavigationRoot)

    __name__ = None
    __parent__ = None

    def __init__(self, request=None):
        self.request = request


class PtahManageRoute(object):
    interface.implements(IPtahManageRoute)

    __name__ = 'ptah-manage'
    __parent__ = DefaultRoot()

    def __init__(self, request):
        self.request = request

        userid = authService.getUserId()
        if not userid:
            raise HTTPForbidden()

        if not ACCESS_MANAGER(userid):
            raise HTTPForbidden()

    def __getitem__(self, key):
        mod = MODULES.get(key)

        if mod is not None:
            return mod(self, self.request)

        raise KeyError(key)


view.pageletType('ptah-module-actions', IPtahModule)

view.registerRoute(
    'ptah-manage-view','/ptah-manage', 
    PtahManageRoute)

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
        self.user = authService.getCurrentPrincipal()

        mod = self.viewcontext
        while not IPtahModule.providedBy(mod):
            mod = getattr(mod, '__parent__', None)
            if mod is None: # pragma: no cover
                break

        self.module = mod


class ManageView(view.View):
    """List ptah modules"""
    view.pyramidView(
        context = IPtahManageRoute,
        route = 'ptah-manage', layout='page',
        template = view.template('ptah:templates/manage.pt'))

    __intr_path__ = '/ptah-manage/index.html'

    def update(self):
        context = self.context
        request = self.request

        mods = []
        for name, mod in MODULES.items():
            mods.append((mod.title, mod))

        mods.sort()
        self.modules = [mod(context, request) for _t, mod in mods]


@view.pyramidView(context = IPtahManageRoute, route = 'ptah-manage-view')
def redirectToManage(request):
    raise HTTPFound(location = '%s/'%request.url)
