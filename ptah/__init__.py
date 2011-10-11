# ptah api

# uri
from ptah.uri import resolve
from ptah.uri import resolver
from ptah.uri import registerResolver
from ptah.uri import extractUriSchema
from ptah.uri import UriGenerator

# manage
from ptah.manage import PtahModule
from ptah.manage import manageModule
from ptah.manage import setAccessManager
from ptah.manage import introspection

# security
from ptah.authentication import authService
from ptah.authentication import registerAuthChecker
from ptah.authentication import registerProvider
from ptah.authentication import registerSearcher
from ptah.authentication import searchPrincipals

from ptah.interfaces import IPrincipal
from ptah.interfaces import IAuthProvider
from ptah.interfaces import IPasswordChanger

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


# create wsgi app
class AppInitialized(object):
    """ This event is beeing sent after new wsgi app is created by
    :py:func:`ptah.make_wsgi_app`.

    .. attribute: app

       New wsgi application object.

    .. attribute: config

       Pyramid `Configuration` object.

    """

    def __init__(self, app, config):
        self.app = app
        self.config = config


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
    from pyramid.config import Configurator

    # configuration
    global_settings.update(settings)
    config = Configurator(settings=global_settings)

    # initialization
    ptah_init(config)

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
    import pyramid_sqla

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
        memphis.config.initializeSettings(settings, configurator)
    except memphis.config.StopException:
        memphis.config.shutdown()
        raise

    # create sql tables
    Base = pyramid_sqla.get_base()
    Base.metadata.create_all()

    # send ApplicationStarting event
    memphis.config.start(configurator)

    # app initialized
    memphis.config.registry.notify(AppInitialized(app, configurator))

    # commit possible transaction
    transaction.commit()
