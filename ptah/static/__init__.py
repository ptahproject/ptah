import logging
from zope.interface import Interface
from bowerstatic import (
    Bower,
    Error,
    InjectorTween,
    PublisherTween,
)
from pyramid.path import AssetResolver


log = logging.getLogger('ptah.static')


class IBower(Interface):
    """ Bower interface
    """


def bower_factory_from_settings(settings):
    prefix = settings.get('ptah.static.prefix', 'ptah.static.')

    bower = Bower()

    bower.publisher_signature = settings.get(
        prefix + 'publisher_signature', 'bowerstatic')
    bower.components_name = settings.get(
        prefix + 'components_name', 'components')

    return bower


def get_bower(request):
    registry = getattr(request, 'registry', None)
    if registry is None:
        registry = request
    return registry.getUtility(IBower)


def bowerstatic_tween_factory(handler, registry):
    bower = get_bower(registry)

    def bowerstatic_tween(request):
        injector_handler = InjectorTween(bower, handler)
        publisher_handler = PublisherTween(bower, injector_handler)

        return publisher_handler(request)

    return bowerstatic_tween


def add_bower_components(config, path, name=None):
    resolver = AssetResolver()
    directory = resolver.resolve(path).abspath()

    bower = get_bower(config.registry)

    if not name:
        name = bower.components_name

    components = bower.components(name, directory)

    log.info("Add bower components '{0}': {1}".format(components.name, path))


def add_bower_component(config, path, version=None, name=None):
    resolver = AssetResolver()
    directory = resolver.resolve(path).abspath()

    bower = get_bower(config.registry)

    if not name:
        name = bower.components_name

    components = bower._component_collections.get(name)

    if not components:
        raise Error("Bower components '{0}' not found.".format(name))

    component = components.load_component(
        directory, 'bower.json', version, version is None)

    components.add(component)

    log.info("Add bower component '{0}': {1}".format(component.name, path))


def include(request, path_or_resource, name=None):
    bower = get_bower(request.registry)

    if not name:
        name = bower.components_name

    components = bower._component_collections.get(name)

    if not components:
        raise Error("Bower components '{0}' not found.".format(name))

    include = components.includer(request.environ)
    include(path_or_resource)


def includeme(config):
    bower = bower_factory_from_settings(config.registry.settings)
    config.registry.registerUtility(bower, IBower)

    config.add_tween('ptah.static.bowerstatic_tween_factory')

    config.add_directive('add_bower_components', add_bower_components)
    config.add_directive('add_bower_component', add_bower_component)

    config.add_request_method(include, 'include')
    config.add_request_method(get_bower, 'get_bower')
