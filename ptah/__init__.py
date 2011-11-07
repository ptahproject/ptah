# ptah api

# uri
from ptah.uri import resolve
from ptah.uri import resolver
from ptah.uri import register_uri_resolver
from ptah.uri import extract_uri_schema
from ptah.uri import UriFactory

# security
from ptah.authentication import authService
from ptah.authentication import SUPERUSER_URI

from ptah.authentication import auth_checker
from ptah.authentication import register_auth_provider

from ptah.authentication import search_principals
from ptah.authentication import principal_searcher
from ptah.authentication import register_principal_searcher

from ptah.interfaces import IACLsAware
from ptah.interfaces import IOwnersAware
from ptah.interfaces import ILocalRolesAware

# acl
from ptah.security import ACL
from ptah.security import ACLsProperty
from ptah.security import get_acls

# role
from ptah.security import Role
from ptah.security import get_roles
from ptah.security import get_local_roles

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
from pyramid.security import NO_PERMISSION_REQUIRED

# password tool
from ptah.password import passwordTool
from ptah.password import password_changer

# rest api
from ptah.rest import restService

# events
from ptah import events

# mail templates
from ptah import mail

# ptah settings
from ptah.settings import PTAH_CONFIG, MAIL

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

# manage
from ptah import manage

# cms
from ptah import cms

# crowd
from ptah import crowd


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
    import ptah
    from pyramid.config import Configurator

    authService.set_userid(SUPERUSER_URI)

    # configuration
    global_settings.update(settings)
    config = Configurator(settings=global_settings)

    # initialization
    try:
        ptah_init(config)
    except Exception, e:
        if isinstance(e, ptah.config.StopException):
            print e.print_tb()

        sys.exit(0)
        return

    # create wsgi app
    return config.make_wsgi_app()


# initialize ptah
def ptah_init(configurator):
    """ Initialize ptah packages.
    Load all ptah packages and intialize ptah settings system.

    This function automatically called by :py:func:`make_wsgi_app` function.
    """
    import ptah
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
        ptah.config.initialize(None, excludes, configurator.registry)

        # load settings
        ptah.config.initialize_settings(settings, configurator)

        # create sql tables
        Base = sqlahelper.get_base()
        Base.metadata.create_all()

        # send AppStarting event
        ptah.config.start(configurator)
    except Exception, e:
        if not isinstance(e, ptah.config.StopException):
            ptah.config.shutdown()
            raise ptah.config.StopException(e)

        ptah.config.shutdown()
        raise

    # commit possible transaction
    transaction.commit()
