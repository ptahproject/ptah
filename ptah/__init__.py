# ptah public api

# module
from ptah.manage import PtahModule
from ptah.interfaces import IPtahModule

from ptah.interfaces import IPtahManageRoute


def initialize(package, pyramid_config, settings):
    from memphis import config

    if pyramid_config is not None:
        pyramid_config.hook_zca()
        pyramid_config.begin()

    if isinstance(package, basestring):
        package = (package,)

    # load packages
    config.initialize(package)

    # load settings
    config.initializeSettings(settings, pyramid_config)

    if pyramid_config is not None:
        pyramid_config.end()
