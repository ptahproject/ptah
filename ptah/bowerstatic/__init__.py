from bowerstatic import (
    Bower,
    Error,
    InjectorTween,
    PublisherTween,
)
from pyramid.path import AssetResolver


class bowerstatic_tween_factory(object):
    def __init__(self, handler, registry):
        self.handler = handler
        self.registry = registry

    def __call__(self, request):
        injector_handler = InjectorTween(
            self.registry.bower,
            self.handler)
        publisher_handler = PublisherTween(
            self.registry.bower,
            injector_handler)

        return publisher_handler(request)


def init_static_components(config, name='components', path=None):
    if not path:
        path = 'ptah:bowerstatic/bower_components'
    resolver = AssetResolver()
    directory = resolver.resolve(path).abspath()
    components = config.registry.bower.components(name, directory)
    local = config.registry.bower.local_components('local', components)


def add_static_component(config, path, version=None):
    resolver = AssetResolver()
    directory = resolver.resolve(path).abspath()
    local = config.registry.bower._component_collections['local']
    local.component(directory, version)


def include(request, path_or_resource):
    local = request.registry.bower._component_collections['local']
    include = local.includer(request.environ)
    include(path_or_resource)


def includeme(config):
    config.registry.bower = Bower()

    config.add_tween('ptah.bowerstatic.bowerstatic_tween_factory')
    config.add_directive('init_static_components', init_static_components)
    config.add_directive('add_static_component', add_static_component)
    config.add_request_method(include, 'include')
