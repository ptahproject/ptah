from pyramid import paster
from pyramid.config import global_registries
from pyramid.request import Request
from pyramid.interfaces import IRequestFactory
from pyramid.threadlocal import manager as threadlocal_manager


def get_app(config_uri):
    from pyramid.router import Router
    from pyramid.config import Configurator

    def make_wsgi_app(self): # pragma: no cover
        self.commit()
        global_registries.add(self.registry)
        return Router(self.registry)

    # ugly hack
    orig = Configurator.make_wsgi_app

    Configurator.make_wsgi_app = make_wsgi_app
    app = paster.get_app(config_uri)
    Configurator.make_wsgi_app = orig
    return app


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
    paster.setup_logging(config_file)

    ptah.POPULATE = False
    return {'app':app, 'registry':registry, 'request': request}
