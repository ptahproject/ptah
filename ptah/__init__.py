# ptah public api

# module
from ptah.manage import PtahModule
from ptah.interfaces import IPtahModule
from ptah.interfaces import IPtahManageRoute

# manage
from ptah.manage import setAccessManager, ACCESS_MANAGER

# security
from ptah import security
from ptah.security import Role, Roles, Permission, registerRole, authService

# batches
from ptah.batch import Batch, Batches, first_neighbours_last

# sqlalchemy query freezer
from ptah.query import QueryFreezer

# create wsgi app
def make_wsgi_app(global_config, **settings):
    from pyramid import path
    from pyramid.config import Configurator

    # configuration
    config = Configurator(settings=settings)

    pkg = path.package_name(path.caller_module())

    # initialization
    initialize(pkg, config, global_config)

    return config.make_wsgi_app()


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
