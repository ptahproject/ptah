from pyramid.security import authenticated_userid
from pyramid.httpexceptions import HTTPFound, HTTPForbidden

import ptah
from ptah import view, config
from ptah.settings import PTAH_CONFIG
from ptah.authentication import authService


MANAGE_ID = 'ptah:manage-module'
INTROSPECT_ID = 'ptah:introspection'


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


def module(id):
    info = config.DirectiveInfo(allowed_scope=('class',))

    def _complete(config, cls, id):
        cls.name = id
        config.storage[MANAGE_ID][id] = cls

    info.attach(
        config.ClassAction(
            _complete, (id,),
            discriminator = (MANAGE_ID, id))
        )


def introspection(id):
    info = config.DirectiveInfo(allowed_scope=('class',))

    def _complete(config, cls, id):
        cls.name = id
        config.storage[INTROSPECT_ID][id] = cls

    info.attach(
        config.ClassAction(
            _complete, (id,),
            discriminator = (INTROSPECT_ID, id))
        )


def PtahAccessManager(id):
    """ default access manager """
    if '*' in PTAH_CONFIG.managers:
        return True

    principal = ptah.resolve(id)

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
        if key not in PTAH_CONFIG.disable_modules:
            mod = config.registry.storage[MANAGE_ID].get(key)

            if mod is not None:
                return mod(self, self.request)

        raise KeyError(key)


view.register_route(
    'ptah-manage-view','/ptah-manage',
    PtahManageRoute, use_global_views=True)

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

        mod = self.request.context
        while not isinstance(mod, PtahModule):
            mod = getattr(mod, '__parent__', None)
            if mod is None: # pragma: no cover
                break

        self.module = mod


class ManageView(view.View):
    """List ptah modules"""
    view.pview(
        context = PtahManageRoute,
        template = view.template('ptah.manage:templates/manage.pt'))

    __intr_path__ = '/ptah-manage/'

    rst_to_html = staticmethod(ptah.rst_to_html)

    def update(self):
        context = self.context
        request = self.request

        mods = []
        for name, mod in config.registry.storage[MANAGE_ID].items():
            if name in PTAH_CONFIG.disable_modules:
                continue
            mods.append((mod.title, mod))

        mods.sort()
        self.modules = [mod(context, request) for _t, mod in mods]


@view.pview(context = PtahManageRoute, route = 'ptah-manage-view')
def redirectToManage(request):
    raise HTTPFound(location = '%s/'%request.url) # pragma: no cover
