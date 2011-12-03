from chameleon import template as chameleon_template

import ptah
from ptah import config


@config.subscriber(ptah.SettingsInitializing)
def initialize(ev):
    cfg = ptah.get_settings('view', ev.registry)
    chameleon_template.AUTO_RELOAD = cfg['chameleon_reload']
    chameleon_template.BaseTemplateFile.auto_reload = cfg['chameleon_reload']
