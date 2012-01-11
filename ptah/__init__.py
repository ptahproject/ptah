# ptah api

try:
    from collections import OrderedDict
except ImportError: # pragma: no cover
    import collections
    from ordereddict import OrderedDict
    collections.OrderedDict = OrderedDict

# config
from ptah import config
from ptah.config import adapter
from ptah.config import subscriber
from ptah.config import get_cfg_storage

# uri
from ptah.uri import resolve
from ptah.uri import resolver
from ptah.uri import extract_uri_schema
from ptah.uri import UriFactory

# sqla
from ptah.sqlautils import get_base
from ptah.sqlautils import get_session
from ptah.sqlautils import reset_session

# events
from ptah import events
from ptah.events import event

# view api
from ptah.view import View
from ptah.view import add_message
from ptah.view import render_messages

from ptah.view import snippet
from ptah.view import render_snippet

# layouts
from ptah.layout import layout
from ptah.layout import wrap_layout

# resource library
from ptah.library import library
from ptah.library import include
from ptah.library import render_includes

# settings
from ptah.settings import get_settings
from ptah.settings import register_settings

# security
from ptah.authentication import auth_service
from ptah.authentication import SUPERUSER_URI

from ptah.authentication import auth_checker
from ptah.authentication import auth_provider

from ptah.authentication import search_principals
from ptah.authentication import principal_searcher

# acl
from ptah.security import ACL
from ptah.security import ACLsProperty
from ptah.security import get_acls
from ptah.interfaces import IACLsAware

# role
from ptah.security import Role
from ptah.security import get_roles
from ptah.security import get_local_roles
from ptah.interfaces import IOwnersAware
from ptah.interfaces import ILocalRolesAware

# permission
from ptah.security import Permission
from ptah.security import get_permissions
from ptah.security import check_permission

# default roles and permissions
from ptah.security import Everyone
from ptah.security import Authenticated
from ptah.security import Owner
from ptah.security import DEFAULT_ACL
from ptah.security import NOT_ALLOWED
from pyramid.security import ALL_PERMISSIONS
from pyramid.security import NO_PERMISSION_REQUIRED

# ptah settings ids
CFG_ID_PTAH = 'ptah'
CFG_ID_FORMAT = 'format'

# password tool
from ptah.password import pwd_tool
from ptah.password import password_changer

# formatter
from ptah.formatter import format, formatter

# rest api
from ptah.rest import RestService

# mail templates
from ptah import mail

# pagination
from ptah.util import Pagination

# thread local data
from ptah.util import tldata

# ReST renderer
from ptah.rst import rst_to_html

# sqlalchemy utils
from ptah.sqlautils import QueryFreezer
from ptah.sqlautils import JsonDictType
from ptah.sqlautils import JsonListType
from ptah.sqla import generate_fieldset
from ptah.sqla import build_sqla_fieldset

# simple ui actions
from ptah.uiactions import uiaction
from ptah.uiactions import list_uiactions

# manage
from ptah import manage

# cms
from ptah import cms

# form api
from ptah import form

# populate
POPULATE = False
from ptah.populate import populate
from ptah.populate import POPULATE_DB_SCHEMA

# simple test case
from ptah.testing import PtahTestCase

# register migration
from ptah.migrate import register_migration

register_migration('ptah', 'ptah:migrations', 'Ptah database migration', True)


def includeme(cfg):
    # auth
    from ptah.security import PtahAuthorizationPolicy
    from pyramid.compat import configparser
    from pyramid.authentication import AuthTktAuthenticationPolicy

    kwargs = {'wild_domain': False,
              'callback': get_local_roles,
              'secret': cfg.registry.settings.get('ptah.secret','')}

    cfg.set_authorization_policy(PtahAuthorizationPolicy())
    cfg.set_authentication_policy(AuthTktAuthenticationPolicy(**kwargs))

    # include extra packages
    cfg.include('pyramid_tm')
    cfg.include('ptah.manage')

    # object events handler
    cfg.registry.registerHandler(
        config.ObjectEventNotify(cfg.registry), (config.IObjectEvent,))

    # initialize settings
    from ptah import settings
    from pyramid.interfaces import PHASE1_CONFIG
    def pyramid_init_settings(cfg, custom_settings=None,
                              section=configparser.DEFAULTSECT):
        cfg.action('ptah.init_settings',
                   settings.init_settings,
                   (cfg, custom_settings, section), order=999999)

    cfg.add_directive('ptah_init_settings', pyramid_init_settings)

    # initialize sql
    from ptah import ptahsettings
    cfg.add_directive('ptah_init_sql', ptahsettings.initialize_sql)

    # ptah manage ui directive
    cfg.add_directive('ptah_init_manage', ptahsettings.enable_manage)

    # ptah mailer directive
    cfg.add_directive('ptah_init_mailer', ptahsettings.set_mailer)

    # ptah rest api directive
    from ptah import rest
    cfg.add_directive('ptah_init_rest', rest.enable_rest_api)

    # ptah.config directives
    from ptah.config import pyramid_get_cfg_storage
    cfg.add_directive(
        'get_cfg_storage', pyramid_get_cfg_storage)

    # ptah.config.settings directives
    from ptah.settings import pyramid_get_settings
    cfg.add_directive(
        'ptah_get_settings', pyramid_get_settings)

    # ptah.authentication directives
    from ptah import authentication
    cfg.add_directive(
        'ptah_auth_checker', authentication.pyramid_auth_checker)
    cfg.add_directive(
        'ptah_auth_provider', authentication.auth_provider.pyramid)
    cfg.add_directive(
        'ptah_principal_searcher', authentication.principal_searcher.pyramid)

    # ptah.uri directives
    cfg.add_directive('ptah_uri_resolver', resolver.pyramid)

    # ptah.password directives
    from ptah import password
    cfg.add_directive('ptah_password_changer', password_changer.pyramid)

    # layout directive
    cfg.add_directive('ptah_layout', layout.pyramid)

    # snippet directive
    cfg.add_directive('ptah_snippet', snippet.pyramid)

    # populate
    def pyramid_populate(cfg):
        from ptah.populate import Populate
        if not POPULATE:
            cfg.action('ptah.populate',
                       Populate(cfg.registry).execute, order=9999999)

    cfg.add_directive('ptah_populate', pyramid_populate)
    cfg.add_directive('ptah_populate_step', populate.pyramid)

    # migrations
    from ptah import migrate
    cfg.add_directive('ptah_migrate', migrate.ptah_migrate)

    # ptah static assets
    cfg.add_static_view('_ptah/static', 'ptah:static/')

    # scan ptah
    cfg.scan('ptah')
