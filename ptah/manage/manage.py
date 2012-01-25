from pyramid.view import view_config
from pyramid.interfaces import IRootFactory
from pyramid.traversal import DefaultRootFactory
from pyramid.httpexceptions import HTTPForbidden

import ptah
from ptah import config

CONFIG_ID = 'ptah.manage:config'
MANAGE_ID = 'ptah.manage:module'
MANAGE_ACTIONS = 'ptah.manage:actions'


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
        return '{0}/{1}'.format(get_manage_url(self.request), self.name)

    @property
    def __name__(self):
        return self.name

    def available(self):
        """ is module available """
        return True


def get_manage_url(request):
    url = request.application_url
    if url.endswith('/'):
        url = url[:-1]

    cfg = ptah.get_settings(ptah.CFG_ID_PTAH, request.registry)
    return '{0}/{1}'.format(url, cfg['manage'])


def module(name):
    info = config.DirectiveInfo()

    def wrapper(cls):
        discr = (MANAGE_ID, name)
        intr = config.Introspectable(MANAGE_ID, discr, cls.title, MANAGE_ID)
        intr['name'] = name
        intr['factory'] = cls
        intr['codeinfo'] = info.codeinfo

        def _complete(cfg, cls, name):
            cls.name = name
            cfg.get_cfg_storage(MANAGE_ID)[name] = cls

        info.attach(
            config.Action(
                _complete, (cls, name),
                discriminator=discr, introspectables=(intr,))
            )
        return cls

    return wrapper


class PtahAccessManager(object):
    """ Allow access to ptah manage for users with specific role and id """

    def __init__(self, registry=None):
        self.cfg = ptah.get_settings(ptah.CFG_ID_PTAH, registry)

    def __call__(self, userid, request):
        managers = self.cfg['managers']

        if userid == ptah.SUPERUSER_URI or '*' in managers:
            return True

        role = self.cfg['manager_role']
        if role:
            root = getattr(request, 'root', None)
            if root is None:
                root_factory = request.registry.queryUtility(
                    IRootFactory, default=DefaultRootFactory)
                root = root_factory(request)

            if role in ptah.get_local_roles(userid, request, root):
                return True

        principal = ptah.resolve(userid)

        if principal is not None and principal.login in managers:
            return True

        return False


def check_access(userid, request):
    manager = ptah.get_settings(ptah.CFG_ID_PTAH).get('access_manager')
    if manager is not None:
        return manager(userid, request)
    return False


def set_access_manager(manager, registry=None):
    ptah.get_settings(ptah.CFG_ID_PTAH, registry)['access_manager'] = manager


class root(object):
    __name__ = None
    __parent__ = None


class PtahManageRoute(object):
    """ ptah management route """

    __name__ = 'ptah-manage'
    __parent__ = root()

    def __init__(self, request):
        self.request = request

        userid = ptah.auth_service.get_userid()
        if not check_access(userid, request):
            raise HTTPForbidden()

        self.userid = userid
        self.cfg = ptah.get_settings(ptah.CFG_ID_PTAH)
        self.__name__ = self.cfg['manage']

        ptah.auth_service.set_effective_userid(ptah.SUPERUSER_URI)

    def __getitem__(self, key):
        if self.cfg['enable_modules']:
            if key in self.cfg['enable_modules']:
                mod = ptah.get_cfg_storage(MANAGE_ID).get(key)
                if mod is not None:
                    return mod(self, self.request)

        elif key not in self.cfg['disable_modules']:
            mod = ptah.get_cfg_storage(MANAGE_ID).get(key)
            if mod is not None:
                return mod(self, self.request)

        raise KeyError(key)


ptah.layout.register(
    '', PtahManageRoute, root=PtahManageRoute, parent='ptah-manage',
    renderer="ptah.manage:templates/ptah-layout.pt")

ptah.layout.register(
    'ptah-page', PtahManageRoute, root=PtahManageRoute, parent='ptah-manage',
    renderer="ptah.manage:templates/ptah-layout.pt")

@ptah.layout(
    'ptah-manage', PtahManageRoute, root=PtahManageRoute,
    renderer="ptah.manage:templates/ptah-manage.pt")

class LayoutManage(ptah.View):
    """ Base layout for ptah manage """

    def update(self):
        self.user = ptah.resolve(self.context.userid)
        self.manage_url = get_manage_url(self.request)

        mod = self.request.context
        while not isinstance(mod, PtahModule):
            mod = getattr(mod, '__parent__', None)
            if mod is None: # pragma: no cover
                break

        self.module = mod
        self.actions = ptah.list_uiactions(mod, self.request, MANAGE_ACTIONS)


@view_config(
    context=PtahManageRoute, wrapper = ptah.wrap_layout(),
    renderer = 'ptah.manage:templates/manage.pt')

class ManageView(ptah.View):
    """List ptah modules"""

    rst_to_html = staticmethod(ptah.rst_to_html)

    def update(self):
        context = self.context
        request = self.request
        self.cfg = ptah.get_settings(ptah.CFG_ID_PTAH, request.registry)

        mods = []
        for name, mod in ptah.get_cfg_storage(MANAGE_ID).items():
            if self.cfg['enable_modules'] and \
                    name not in self.cfg['enable_modules']:
                continue
            if name in self.cfg['disable_modules']:
                continue

            mod = mod(context, request)
            if not mod.available():
                continue
            mods.append((mod.title, mod))

        self.modules = [mod for _t, mod in sorted(mods)]
