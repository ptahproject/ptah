import os
import logging
import venusian
from pyramid.path import AssetResolver
from pyramid.registry import Introspectable
from pyramid.exceptions import ConfigurationError
from pyramid.interfaces import IViewMapperFactory
from pyramid.config.views import DefaultViewMapper

log = logging.getLogger('ptah.renderer')

ID_LAYER = 'ptah.renderer:layer'


def add_layer(cfg, layer, name='', path='', description=''):
    """ add new layer

    :param layer: layer id
    :param name: name
    :param path: asset path
    :param description: module description
    """
    if not path:
        raise ConfigurationError('Path is required')

    discr = (ID_LAYER, name, layer)

    resolver = AssetResolver()
    directory = resolver.resolve(path).abspath()

    intr = Introspectable(ID_LAYER, discr, name, 'ptah.renderer-layer')
    intr['name'] = name
    intr['layer'] = layer
    intr['path'] = directory
    intr['asset'] = path
    intr['description'] = description
    intr['filters'] = {}

    storage = cfg.registry.setdefault(ID_LAYER, {})
    layers = storage.setdefault(layer, [])
    layers.insert(0, intr)

    cfg.action(discr, introspectables=(intr,))
    log.info("Add layer: %s path:%s"%(layer, path))


def add_layers(cfg, name='', path='', description=''):
    """ add new layers, read directory use first level folders
    as layer name

    :param name: name
    :param path: asset path
    :param description: module description
    """
    resolver = AssetResolver()
    directory = resolver.resolve(path).abspath()

    for layer in os.listdir(directory):
        layer_path = os.path.join(directory, layer)
        if os.path.isdir(layer_path):
            add_layer(cfg, layer, name, layer_path, description)


def add_tmpl_filter(cfg, template, callable, name='', description=''):
    view = cfg.maybe_dotted(callable)

    mapper = cfg.registry.queryUtility(IViewMapperFactory)
    if mapper is None:
        mapper = DefaultViewMapper

    mapped_view = mapper()(view)
    layer, template = template.split(':', 1)

    def action():
        storage = cfg.registry.get(ID_LAYER, {})
        layers = storage.get(layer, [])
        for intr in layers:
            if intr['name'] == name:
                intr['filters'][template] = mapped_view
                return

        raise ConfigurationError(
            "Can't find layer: %s%s"%(layer, '(%s)'%name if name else ''))

    cfg.action((ID_LAYER, 'filter', layer, template, name), action)


class tmpl_filter(object):

    def __init__(self, template, name='', description=''):
        self.template = template
        self.name = name
        self.description = description

    def __call__(self, wrapped):
        def callback(context, name, ob):
            cfg = context.config.with_package(info.module)
            add_tmpl_filter(
                cfg, self.template, ob, self.name, self.description)

        info = venusian.attach(wrapped, callback, category='ptah.renderer')

        return wrapped


def change_layers_order(cfg, info):
    """ change layers order """
    storage = cfg.registry.setdefault(ID_LAYER, {})
    for name, layers in info.items():
        data = storage.get(name)
        if not data:
            log.warning('layer.order.%s setting is not found'%name)
            continue

        def in_data(name, data):
            for intr in data:
                if intr['name'] == name:
                    return intr
            return None

        new_data = []
        for l in layers:
            intr = in_data(l, data)
            if intr:
                new_data.append(intr)

        new_data.extend([intr for intr in data if intr not in new_data])

        storage[name] = new_data
