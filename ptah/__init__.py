# ptah api

# uri
from ptah.uri import resolve
from ptah.uri import resolver
from ptah.uri import register_uri_resolver
from ptah.uri import extract_uri_schema
from ptah.uri import UriGenerator

# manage
from ptah.manage import PtahModule
from ptah.manage import manageModule
from ptah.manage import introspection
from ptah.manage import set_access_manager
from ptah.manage import get_access_manager

# security
from ptah.authentication import authService
from ptah.authentication import SUPERUSER_URI

from ptah.authentication import register_auth_checker
from ptah.authentication import register_auth_provider

from ptah.authentication import search_principals
from ptah.authentication import principal_searcher
from ptah.authentication import register_principal_searcher

from ptah.interfaces import IACLsAware
from ptah.interfaces import IOwnersAware
from ptah.interfaces import ILocalRolesAware

# acl
from ptah.security import ACL
from ptah.security import ACLs
from ptah.security import ACLsProperty

# role
from ptah.security import Role
from ptah.security import Roles
from ptah.security import LocalRoles

# permission
from ptah.security import Permission
from ptah.security import Permissions
from ptah.security import checkPermission

# default roles and permissions
from ptah.security import Everyone
from ptah.security import Authenticated
from ptah.security import Owner
from ptah.security import DEFAULT_ACL
from ptah.security import NOT_ALLOWED
from pyramid.security import NO_PERMISSION_REQUIRED

# password tool
from ptah.password import passwordTool

# rest api
from ptah.rest import restService

# events
from ptah import events

# mail api
from ptah import mail

# ptah settings
from ptah.settings import PTAH_CONFIG

# pagination
from ptah.util import Pagination

# thread local data
from ptah.util import tldata

# sqlalchemy utils
from ptah.sqla import QueryFreezer
from ptah.sqla import JsonDictType
from ptah.sqla import JsonListType
from ptah.sqla import generateFieldset
from ptah.sqla import buildSqlaFieldset


def includeme(config):
    config.add_directive('ptah_init', ptah_init)


def make_wsgi_app(global_settings, **settings):
    """ Create wsgi application, this function initialize
    `ptah` and sends :py:class:`AppInitialized` event.
    It is possible to use this function as entry point for paster based
    deployment::

      [app:myapp]
      use = egg:ptah#app

    """
    import sys
    import memphis
    from pyramid.config import Configurator

    authService.set_userid(SUPERUSER_URI)

    # configuration
    global_settings.update(settings)
    config = Configurator(settings=global_settings)

    # initialization
    try:
        ptah_init(config)
    except Exception, e:
        if isinstance(e, memphis.config.StopException):
            print e.print_tb()

        sys.exit(0)

    # create wsgi app
    return config.make_wsgi_app()


# initialize memphis
def ptah_init(configurator):
    """ Initialize memphis packages.
    Load all memphis packages and intialize memphis settings system.

    This function automatically called by :py:func:`make_wsgi_app` function.
    """
    import memphis
    import transaction
    import sqlahelper

    configurator.include('pyramid_tm')

    try:
        settings = configurator.registry.settings

        # exclude
        excludes = []
        if 'ptah.excludes' in settings:
            excludes.extend(s.strip()
                            for s in settings['ptah.excludes'].split())

        # load packages
        memphis.config.initialize(None, excludes, configurator.registry)

        # load settings
        memphis.config.initialize_settings(settings, configurator)

        # create sql tables
        Base = sqlahelper.get_base()
        Base.metadata.create_all()

        # send AppStarting event
        memphis.config.start(configurator)
    except Exception, e:
        if not isinstance(e, memphis.config.StopException):
            memphis.config.shutdown()
            raise memphis.config.StopException(e)

        memphis.config.shutdown()
        raise

    # commit possible transaction
    transaction.commit()
