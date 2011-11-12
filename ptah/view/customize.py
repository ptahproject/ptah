import colander
from chameleon import template as chameleon_template

from ptah import config


TEMPLATE = config.register_settings(
    'template',

    config.SchemaNode(
        colander.Bool(),
        name = 'chameleon_reload',
        default = False,
        title = 'Auto reload',
        description = 'Enable chameleon templates auto reload.'),

    title = 'Templates settings',
    )


class _ViewLayersManager(object):

    def __init__(self):
        self.layers = {}

    def register(self, layer, discriminator):
        data = self.layers.setdefault(discriminator, [])
        if not layer:
            data.insert(0, layer)
        else:
            data.append(layer)

    def enabled(self, layer, discriminator):
        data = self.layers.get(discriminator)
        if data:
            return data[-1] == layer
        return False

_layersManager = _ViewLayersManager()


class LayerWrapper(object):

    def __init__(self, callable, discriminator):
        self.callable = callable
        self.layer = discriminator[-1]
        self.discriminator = discriminator[:-1]
        _layersManager.register(self.layer, self.discriminator)

    def __call__(self, cfg, *args, **kw):
        if not _layersManager.enabled(self.layer, self.discriminator):
            return # pragma: no cover

        self.callable(cfg, *args, **kw)


@config.subscriber(config.SettingsInitializing)
def initialize(*args):
    chameleon_template.AUTO_RELOAD = TEMPLATE.chameleon_reload
    chameleon_template.BaseTemplateFile.auto_reload = \
        TEMPLATE.chameleon_reload
