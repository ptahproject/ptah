# ptah.renderer public api

__all__ = ['tmpl_filter', 'layout', 'layout_config', 'add_message',
           'render', 'RendererNotFound', 'includeme']

try:
    from collections import OrderedDict
except ImportError: # pragma: no cover
    import collections
    from ordereddict import OrderedDict
    collections.OrderedDict = OrderedDict

from ptah.renderer.layer import tmpl_filter
from ptah.renderer.layout_impl import layout
from ptah.renderer.layout_impl import layout_config
from ptah.renderer.renderer import render
from ptah.renderer.renderer import RendererNotFound


def includeme(cfg):
    cfg.include('pyramid_chameleon')

    import os
    from pyramid.path import AssetResolver
    from pyramid.settings import aslist
    from pyramid.exceptions import ConfigurationError

    from ptah.renderer.renderer import lt_renderer_factory
    from ptah.renderer.layer import add_layer, add_layers, change_layers_order
    from ptah.renderer.layer import add_tmpl_filter
    from ptah.renderer.layout_impl import add_layout, set_layout_data

    # config directives
    cfg.add_directive('add_layer', add_layer)
    cfg.add_directive('add_layers', add_layers)
    cfg.add_directive('add_layout', add_layout)
    cfg.add_directive('add_tmpl_filter', add_tmpl_filter)

    # request.render_tmpl
    cfg.add_request_method(render, 'render_tmpl')

    # request.set_layout_data
    cfg.add_request_method(set_layout_data, 'set_layout_data')

    def get_layout_data(request):
        return {}
    cfg.add_request_method(get_layout_data, 'layout_data', True, True)

    # renderer factory
    cfg.add_renderer('.lt', lt_renderer_factory)

    # layout renderer
    cfg.add_renderer('ptah.renderer:layout', layout)

    # order
    settings = cfg.get_settings()

    order = {}
    for key, val in settings.items():
        if key.startswith('layer.order.'):
            layer = key[12:]
            order[layer] = [s.strip() for s in aslist(val)]

    if order:
        cfg.action(
            'ptah.renderer.order',
            change_layers_order, (cfg, order), order=999999+1)

    # global custom layer
    custom = settings.get('layer.custom', '').strip()
    if custom:
        resolver = AssetResolver()
        directory = resolver.resolve(custom).abspath()
        if not os.path.isdir(directory):
            raise ConfigurationError(
                "Directory is required for layer.custom setting: %s"%custom)

        cfg.action(
            'ptah.renderer.custom',
            add_layers, (cfg, 'layer_custom', custom), order=999999+2)

    # scan
    cfg.scan('ptah.renderer')
