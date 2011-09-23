# ptah api

# uri
from ptah.uri import resolve
from ptah.uri import registerResolver
from ptah.uri import extractUriType
from ptah.uri import UUIDGenerator

# manage
from ptah.manage import PtahModule, IPtahModule
from ptah.manage import setAccessManager, ACCESS_MANAGER

# security
from ptah.authentication import authService
from ptah.authentication import checkPermission
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

# role
from ptah.security import ACL
from ptah.security import ACLs
from ptah.security import ACLsProperty
from ptah.security import Role
from ptah.security import Roles
from ptah.security import LocalRoles

# permission
from ptah.security import Permission
from ptah.security import Permissions

# default roles and permissions
from ptah.security import Everyone
from ptah.security import Authenticated
from ptah.security import Owner
from ptah.security import DEFAULT_ACL

# password tool
from ptah.password import passwordTool

# rest api
from ptah.rest import RestException
from ptah.rest import registerService
from ptah.rest import registerServiceAction
from ptah.interfaces import IRestServiceAction

# events
from ptah import events

# mail api
from ptah import mail

# ptah settnigs
from ptah.settings import PTAH_CONFIG

# batches
from ptah.batch import Batch, Batches, first_neighbours_last

# sqlalchemy query freezer
from ptah.query import QueryFreezer

# create wsgi app
class WSGIAppInitialized(object):
    
    def __init__(self, app, config):
        self.app = app
        self.config = config


def make_wsgi_app(global_config, **settings):
    import transaction
    import pyramid_sqla
    from pyramid import path
    from pyramid.config import Configurator
    
    # configuration
    config = Configurator(settings=settings)

    # initialization
    initialize(None, config, global_config)

    # create wsgi app
    app = config.make_wsgi_app()

    # create sql tables
    Base = pyramid_sqla.get_base()
    Base.metadata.create_all()

    # event
    config.begin()
    config.registry.notify(WSGIAppInitialized(app, config))
    config.end()
    config.commit()

    # commit possible transaction
    transaction.commit()

    return app


# initialize memphis
def initialize(package, pyramid_config, settings):
    from memphis import config

    pyramid_config.begin()

    if isinstance(package, basestring):
        package = (package,)

    # exclude
    excludes = []
    if 'excludes' in pyramid_config.registry.settings:
        excludes.extend(s.strip() for s in
                        pyramid_config.registry.settings['excludes'].split())

    if 'excludes' in settings:
        excludes.extend(s.strip() for s in settings['excludes'].split())

    # load packages
    config.initialize(package, excludes, pyramid_config.registry)

    # load settings
    config.initializeSettings(settings, pyramid_config)
