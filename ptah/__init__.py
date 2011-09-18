# ptah public api

# uri
from ptah.uri import resolve
from ptah.uri import registerResolver
from ptah.uri import extractUriType
from ptah.uri import UUIDGenerator

# module
from ptah.manage import PtahModule
from ptah.interfaces import IPtahModule
from ptah.interfaces import IPtahManageRoute

# manage
from ptah.manage import setAccessManager, ACCESS_MANAGER

# security
from ptah import security
from ptah.security import View
from ptah.security import Role, Roles, Permission, registerRole, authService
from ptah.security import checkPermission

# rest api
from ptah.rest import RestException
from ptah.rest import registerService
from ptah.rest import registerServiceAction
from ptah.interfaces import IRestServiceAction

# mail api
from ptah import mail

# ptah settnigs
from ptah.settings import PTAH

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

    pyramid_config.hook_zca()
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
    config.initialize(package, excludes)

    # load settings
    config.initializeSettings(settings, pyramid_config)

    pyramid_config.end()
