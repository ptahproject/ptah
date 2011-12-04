""" routes """
from ptah import config
from pyramid.config.util import make_predicates
from pyramid.request import route_request_iface
from pyramid.urldispatch import RoutesMapper
from pyramid.interfaces import IRequest, IRouteRequest, IRoutesMapper


def register_route(name, pattern=None, factory=None, header=None,
                   traverse=None, pregenerator=None,
                   use_global_views=False, derived_route=None,
                   xhr=False, request_method=None,
                   path_info=None, request_param=None,
                   accept=None, custom_predicates=()):

    # these are route predicates; if they do not match, the next route
    # in the routelist will be tried
    ignored, predicates, ignored = make_predicates(
        xhr=xhr,
        request_method=request_method,
        path_info=path_info,
        request_param=request_param,
        header=header,
        accept=accept,
        traverse=traverse,
        custom=custom_predicates)

    info = config.DirectiveInfo()
    info.attach(
        config.Action(
            register_route_impl,
            (name, pattern, factory, predicates, pregenerator,
             use_global_views, derived_route),
            discriminator = ('ptah.view:route', name),
            ))


def register_route_impl(cfg, name, pattern, factory, predicates,
                        pregenerator, use_global_views, derived_route):
    registry = cfg.registry

    request_iface = registry.queryUtility(IRouteRequest, name=name)
    if request_iface is None:
        if use_global_views:
            bases = (IRequest,)
        else:
            bases = ()

        if derived_route is not None:
            bases = (registry.getUtility(IRouteRequest,
                                         name=derived_route),) + bases

        request_iface = route_request_iface(name, bases)
        registry.registerUtility(request_iface, IRouteRequest, name=name)

    mapper = registry.queryUtility(IRoutesMapper)
    if mapper is None:
        mapper = RoutesMapper()
        registry.registerUtility(mapper, IRoutesMapper)

    return mapper.connect(name, pattern, factory, predicates=predicates,
                          pregenerator=pregenerator, static=False)
