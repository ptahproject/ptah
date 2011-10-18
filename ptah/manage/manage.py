from ptah import view, config
from pyramid.security import authenticated_userid
from pyramid.httpexceptions import HTTPFound, HTTPForbidden

from ptah import resolve
from ptah.settings import PTAH_CONFIG
from ptah.authentication import authService


MODULES = {}

class PtahModule(object):

    #: Module name (also is used for url generation)
    name = ''

    #: Module title
    title = ''

    def __init__(self, manager, request):
        self.__parent__ = manager
        self.request = request

    def url(self):
        """ return url to this module """
        return '%s/'%self.name

    @property
    def __name__(self):
        return self.name

    def available(self):
        """ is module available """
        return True


def manageModule(id):
    info = config.DirectiveInfo(allowed_scope=('class',))

    def _complete(config, cls, id):
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

    def _complete(config, cls, id):
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

def set_access_manager(func):
    global ACCESS_MANAGER
    ACCESS_MANAGER = func


def get_access_manager():
    return ACCESS_MANAGER


class PtahManageRoute(object):
    """ ptah management route """

    __name__ = 'ptah-manage'
    __parent__ = None

    def __init__(self, request):
        self.request = request

        userid = authService.get_userid()
        if not userid:
            raise HTTPForbidden()

        if not ACCESS_MANAGER(userid):
            raise HTTPForbidden()

    def __getitem__(self, key):
        mod = MODULES.get(key)

        if mod is not None:
            return mod(self, self.request)

        raise KeyError(key)


view.register_route(
    'ptah-manage-view','/ptah-manage',
    PtahManageRoute)

view.register_route(
    'ptah-manage','/ptah-manage/*traverse',
    PtahManageRoute, use_global_views=True)

view.snippettype('ptah-module-actions', PtahModule)

view.register_snippet(
    'ptah-module-actions', PtahModule,
    template = view.template('ptah.manage:templates/moduleactions.pt'))

view.register_layout(
    '', PtahManageRoute, parent='ptah-manage',
    template=view.template("ptah.manage:templates/ptah-layout.pt"))


class LayoutManage(view.Layout):
    view.layout('ptah-manage', PtahManageRoute,
                template=view.template("ptah.manage:templates/ptah-manage.pt"))

    def update(self):
        self.user = authService.get_current_principal()

        mod = self.viewcontext
        while not isinstance(mod, PtahModule):
            mod = getattr(mod, '__parent__', None)
            if mod is None: # pragma: no cover
                break

        self.module = mod


class ManageView(view.View):
    """List ptah modules"""
    view.pview(
        context = PtahManageRoute,
        route = 'ptah-manage', layout='ptah-manage',
        template = view.template('ptah.manage:templates/manage.pt'))

    __intr_path__ = '/ptah-manage/'

    def update(self):
        context = self.context
        request = self.request

        mods = []
        for name, mod in MODULES.items():
            mods.append((mod.title, mod))

        mods.sort()
        self.modules = [mod(context, request) for _t, mod in mods]


@view.pview(context = PtahManageRoute, route = 'ptah-manage-view')
def redirectToManage(request):
    raise HTTPFound(location = '%s/'%request.url) # pragma: no cover
