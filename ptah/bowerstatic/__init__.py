import bowerstatic


class tween_factory(object):
    def __init__(self, handler, registry):
        self.handler = handler
        self.registry = registry

    def __call__(self, request):
        injector_handler = bowerstatic.InjectorTween(
            self.registry.bower, self.handler)
        publisher_handler = bowerstatic.PublisherTween(
            self.registry.bower, injector_handler)

        return publisher_handler(request)

def init_bowerstatic(config, path):
    name = config.registry.settings['bowerstatic.components_name']
    config.registry.bower.components(name, path)


def include(request, path_or_resource):
    name = request.registry.settings['bowerstatic.components_name']
    bower = request.registry.bower
    components = bower._component_collections.get(name)
    if not components:
        raise bowerstatic.Error("Component collection '%s' missing." % name)
    include = components.includer(request.environ)
    include(path_or_resource)


def includeme(config):

    config.registry.settings['bowerstatic.components_name'] = 'components'
    config.registry.bower = bowerstatic.Bower()

    config.add_directive('init_bowerstatic', init_bowerstatic)
    config.add_tween('ptah.bowerstatic.tween_factory')
    config.add_request_method(include, 'include')
