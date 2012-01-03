from pyramid.config import global_registries
from pyramid.paster import get_app
from pyramid.paster import setup_logging
from pyramid.request import Request
from pyramid.interfaces import IRequestFactory
from pyramid.threadlocal import manager as threadlocal_manager


def bootstrap(config_uri):
    import ptah
    ptah.POPULATE = True

    app = get_app(config_uri)
    registry = global_registries.last

    request_factory = registry.queryUtility(IRequestFactory, default=Request)
    request = request_factory.blank('/')
    request.registry = registry

    threadlocals = {'registry':registry, 'request':request}
    threadlocal_manager.push(threadlocals)

    config_file = config_uri.split('#', 1)[0]
    setup_logging(config_file)

    ptah.POPULATE = False
    return {'app':app, 'registry':registry, 'request': request}
