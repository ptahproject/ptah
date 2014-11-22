import os
from pyramid.interfaces import IRendererFactory
from pyramid.renderers import RendererHelper

from .layer import ID_LAYER

ID_TEMPLATE = 'ptah.renderer:template'
ID_TEMPLATE_EXT = 'ptah.renderer:template-ext'


class RendererNotFound(ValueError):
    """ Renderer is not found """


def render(request, asset, context=None, **options):
    registry = request.registry

    if context is not None:
        options['context'] = context

    templates = registry.get(ID_TEMPLATE)
    if templates is None:
        templates = registry[ID_TEMPLATE] = {}
        registry[ID_TEMPLATE_EXT] = tuple(
            name for name, _ in
            registry.getUtilitiesFor(IRendererFactory) if name.startswith('.'))

    if asset not in templates:
        r_name = None
        for ext in registry[ID_TEMPLATE_EXT]:
            if asset.endswith(ext):
                r_name = asset

        if not r_name:
            r_name = '%s.lt'%asset

        templates[asset] = RendererHelper(r_name, registry=registry)

    view = getattr(request, '__view__', None)
    if view is None:
        view = context

    request.__view__ = view

    options['view'] = view
    system = {'view': view,
              'renderer_info': templates[asset],
              'context': context,
              'request': request}

    result = templates[asset].render(options, system, request)

    request.__view__ = view
    return result


class template(object):

    def __init__(self, asset):
        self.asset = asset

    def __call__(self, request, context=None, **options):
        return render(request, self.asset, context, **options)


class renderer(object):

    def __init__(self, rendr, filter):
        self.rendr = rendr
        self.filter = filter

    def __call__(self, value, system):
        value.update(self.filter(system['context'], system['request']))
        return self.rendr(value, system)


def lt_renderer_factory(info):
    registry = info.registry

    layer, name = info.name.split(':', 1)
    name = name[:-3]

    storage = registry.get(ID_LAYER)
    if not storage or layer not in storage:
        raise ValueError('Layer is not found: "%s"'%layer)

    factories = dict(
        (name, factory) for name, factory in
        registry.getUtilitiesFor(IRendererFactory) if name.startswith('.'))

    layer_data = storage[layer]

    # filter
    filter = None
    for intr in layer_data:
        if name in intr['filters']:
            filter = intr['filters'][name]
            break

    # search template
    for intr in layer_data:
        for ext, factory in factories.items():
            fname = os.path.join(intr['path'], '%s%s'%(name, ext))
            if os.path.exists(fname):
                info.name = fname
                if filter is not None:
                    return renderer(factory(info), filter)
                else:
                    return factory(info)

    raise RendererNotFound(
        'Missing template layer renderer: %s:%s' % (layer, name))
