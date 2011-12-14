# ptah api

# uri
from ptah.uri import resolve
from ptah.uri import resolver
from ptah.uri import register_uri_resolver
from ptah.uri import extract_uri_schema
from ptah.uri import UriFactory

# config
from ptah import config
from ptah.config import adapter
from ptah.config import subscriber
from ptah.config import get_cfg_storage

# events
from ptah import events
from ptah.events import event

# view api
from ptah.view import View
from ptah.view import add_message
from ptah.view import render_messages

from ptah.view import snippet
from ptah.view import register_snippet
from ptah.view import render_snippet

# layouts
from ptah.layout import layout
from ptah.layout import register_layout
from ptah.layout import wrap_layout

# resource library
from ptah.library import library
from ptah.library import include
from ptah.library import render_includes

# settings
from ptah.settings import get_settings
from ptah.settings import register_settings
from ptah.settings import init_settings

# security
from ptah.authentication import auth_service
from ptah.authentication import SUPERUSER_URI

from ptah.authentication import auth_checker
from ptah.authentication import auth_provider
from ptah.authentication import register_auth_provider

from ptah.authentication import search_principals
from ptah.authentication import principal_searcher
from ptah.authentication import register_principal_searcher

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
CFG_ID_SQLA = 'sqla'
CFG_ID_PASSWORD = 'password'

# password tool
from ptah.password import pwd_tool
from ptah.password import password_changer

# formatter
from ptah.formatter import format, formatter

# rest api
from ptah.rest import RestService
from ptah.rest import enable_rest_api

# events
from ptah import events

# mail templates
from ptah import mail

# pagination
from ptah.util import Pagination

# thread local data
from ptah.util import tldata

# ReST renderer
from ptah.rst import rst_to_html

# sqlalchemy utils
from ptah.sqla import QueryFreezer
from ptah.sqla import JsonDictType
from ptah.sqla import JsonListType
from ptah.sqla import generate_fieldset
from ptah.sqla import build_sqla_fieldset

# simple ui actions
from ptah.uiactions import uiaction
from ptah.uiactions import list_uiactions

# manage
from ptah import manage

# cms
from ptah import cms
from ptah.cms import Session

# form api
from ptah import form

# simple test case
from ptah.testing import PtahTestCase


def includeme(cfg):
    # auth
    from ptah.security import PtahAuthorizationPolicy
    from pyramid.authentication import AuthTktAuthenticationPolicy

    kwargs = {'wild_domain': False,
              'callback': get_local_roles,
              'secret': cfg.registry.settings.get('ptah.secret','')}

    cfg.set_authorization_policy(PtahAuthorizationPolicy())
    cfg.set_authentication_policy(AuthTktAuthenticationPolicy(**kwargs))

    # include extra packages
    cfg.include('pyramid_tm')
    cfg.include('ptah.manage')

    # directive
    cfg.add_directive('ptah_initialize', ptah_initialize)

    # object events handler
    cfg.registry.registerHandler(
        config.ObjectEventNotify(cfg.registry), (config.IObjectEvent,))

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
        'ptah_auth_provider', authentication.pyramid_auth_provider)
    cfg.add_directive(
        'ptah_principal_searcher', authentication.pyramid_principal_searcher)

    # ptah.uri directives
    from ptah import uri
    cfg.add_directive(
        'ptah_uri_resolver', uri.pyramid_uri_resolver)

    # ptah.password directives
    from ptah import password
    cfg.add_directive(
        'ptah_password_changer', password.pyramid_password_changer)

    # ptah rest api directive
    from ptah import rest
    cfg.add_directive(
        'ptah_rest_api', rest.enable_rest_api)

    # ptah mailer directive
    from ptah import ptahsettings
    cfg.add_directive(
        'ptah_mailer', ptahsettings.set_mailer)

    # ptah static assets
    cfg.add_static_view('_ptah/static', 'ptah:static/')

    # scan ptah
    cfg.scan('ptah')


# initialize ptah
def ptah_initialize(cfg):
    """ Initialize ptah package."""
    from pyramid.exceptions import  ConfigurationExecutionError

    cfg.begin()
    try:
        auth_service.set_userid(SUPERUSER_URI)

        # initialize settings
        init_settings(cfg, cfg.registry.settings)

    except config.StopException:
        config.shutdown()
        raise
    finally:
        cfg.end()
