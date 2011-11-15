import colander
from pyramid.httpexceptions import HTTPForbidden

import ptah
from ptah import view, config
from ptah.authentication import authService

CONFIG_ID = 'ptah.manage:config'
MANAGE_ID = 'ptah.manage:module'
INTROSPECT_ID = 'ptah.manage:introspection'

CONFIG = config.register_settings(
    'manage',

    config.SchemaNode(
        config.Sequence(), colander.SchemaNode(colander.Str()),
        name = 'managers',
        title = 'Managers',
        description = 'List of user logins with access rights to '\
            'ptah management ui.',
        default = ()),

    config.SchemaNode(
        colander.Str(),
        name = 'manage_url',
        title = 'Ptah manage url',
        default = '/ptah-manage'),

    config.SchemaNode(
        config.Sequence(), colander.SchemaNode(colander.Str()),
        name = 'disable_modules',
        title = 'Hide Modules in Management UI',
        description = 'List of modules names to hide in manage ui',
        default = ()),

    config.SchemaNode(
        config.Sequence(), colander.SchemaNode(colander.Str()),
        name = 'disable_models',
        title = 'Hide Models in Model Management UI',
        description = 'List of models to hide in model manage ui',
        default = ('cms-type:sqlblob',)),

    title = 'Ptah manage settings',
    )


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
        return '%s/%s'%(CONFIG.manage_url, self.name)

    @property
    def __name__(self):
        return self.name

    def available(self):
        """ is module available """
        return True


def module(id):
    info = config.DirectiveInfo(allowed_scope=('class',))

    def _complete(cfg, cls, id):
        cls.name = id
        cfg.get_cfg_storage(MANAGE_ID)[id] = cls

    info.attach(
        config.ClassAction(
            _complete, (id,),
            discriminator = (MANAGE_ID, id))
        )


def introspection(id):
    info = config.DirectiveInfo(allowed_scope=('class',))

    def _complete(cfg, cls, id):
        cls.name = id
        cfg.get_cfg_storage(INTROSPECT_ID)[id] = cls

    info.attach(
        config.ClassAction(
            _complete, (id,),
            discriminator = (INTROSPECT_ID, id))
        )


def PtahAccessManager(id):
    """ default access manager """
    managers = CONFIG.managers

    if '*' in managers:
        return True

    principal = ptah.resolve(id)

    if principal is not None and principal.login in managers:
        return True

    return False


def check_access(userid):
    return CONFIG.get('access_manager', PtahAccessManager)(userid)


def set_access_manager(func):
    CONFIG['access_manager'] = func


class PtahManageRoute(object):
    """ ptah management route """

    def __init__(self, request):
        self.request = request

        userid = authService.get_userid()
        if not check_access(userid):
            raise HTTPForbidden()

        self.manage_url = CONFIG.manage_url

    def __getitem__(self, key):
        if key not in CONFIG.disable_modules:
            mod = config.get_cfg_storage(MANAGE_ID).get(key)

            if mod is not None:
                return mod(self, self.request)

        raise KeyError(key)


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
        self.manage_url = CONFIG.manage_url
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
        for name, mod in config.get_cfg_storage(MANAGE_ID).items():
            if name in CONFIG.disable_modules:
                continue
            mods.append((mod.title, mod))

        mods.sort()
        self.modules = [mod(context, request) for _t, mod in mods]
