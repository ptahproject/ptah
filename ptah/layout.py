""" layout implementation """
from collections import namedtuple
from zope.interface import providedBy, Interface

from pyramid.compat import text_, string_types
from pyramid.config.views import DefaultViewMapper
from pyramid.httpexceptions import HTTPException
from pyramid.location import lineage
from pyramid.renderers import RendererHelper
from pyramid.interfaces import IRequest
from pyramid.interfaces import IRouteRequest
from pyramid.interfaces import IView
from pyramid.interfaces import IViewClassifier

from ptah import config
from ptah.view import View

LAYOUT_ID = 'ptah.view:layout'
LAYOUT_WRAPPER_ID = 'ptah.view:layout-wrapper'

LayoutInfo = namedtuple(
    'LayoutInfo', 'name layout view original renderer action')


class ILayout(Interface):
    """ marker interface """


def query_layout(context, request, name=''):
    """ query named layout for context """
    assert IRequest.providedBy(request), "must pass in a request object"

    try:
        iface = request.request_iface
    except AttributeError:
        iface = IRequest

    adapters = request.registry.adapters

    for context in lineage(context):
        layout_factory = adapters.lookup(
            (providedBy(context), iface), ILayout, name=name)

        if layout_factory is not None:
            return layout_factory, context

    return None, None


def query_layout_chain(context, request, layoutname=''):
    chain = []

    layout, layoutcontext = query_layout(context, request, layoutname)
    if layout is None:
        return chain

    chain.append((layout, layoutcontext))
    contexts = {layoutname: layoutcontext}

    while layout is not None:
        if layout.layout in contexts:
            l_context = contexts[layout.layout].__parent__
        else:
            l_context = layoutcontext

        layout, layoutcontext = query_layout(l_context, request, layout.layout)
        if layout is not None:
            chain.append((layout, layoutcontext))
            contexts[layout.name] = layoutcontext

            if layout.layout is None:
                break

    return chain


def layout(name='', context=None, parent='',
           renderer=None, route_name=None, layer=''):
    info = config.DirectiveInfo()

    def wrapper(view):
        discr = (LAYOUT_ID, name, context, route_name, layer)

        intr = config.Introspectable(LAYOUT_ID, discr, name, LAYOUT_ID)
        intr['name'] = name
        intr['view'] = view
        intr['context'] = context
        intr['layer'] = layer
        intr['renderer'] = renderer
        intr['route_name'] = route_name
        intr['parent'] = parent
        intr['codeinfo'] = info.codeinfo

        info.attach(
            config.Action(
                config.LayerWrapper(register_layout_impl, discr),
                (view, name, context, renderer, parent, route_name),
                discriminator=discr, introspectables=(intr,))
            )
        return view

    return wrapper


def register_layout(
    name='', context=None, parent='',
    view=View, renderer=None, route_name=None, layer=''):

    discr = (LAYOUT_ID, name, context, route_name, layer)

    intr = config.Introspectable(LAYOUT_ID, discr, name, LAYOUT_ID)
    intr['name'] = name
    intr['view'] = view
    intr['context'] = context
    intr['layer'] = layer
    intr['renderer'] = renderer
    intr['route_name'] = route_name
    intr['parent'] = parent

    info = config.DirectiveInfo()
    info.attach(
        config.Action(
            config.LayerWrapper(register_layout_impl, discr),
            (view, name, context, renderer, parent, route_name),
            discriminator=discr, introspectables=(intr,))
        )


def register_layout_impl(cfg, view, name, context, renderer,layout,route_name):
    if not layout:
        layout = None
    elif layout == '.':
        layout = ''

    if isinstance(renderer, string_types):
        renderer = RendererHelper(name=renderer, registry=cfg.registry)

    request_iface = IRequest
    if route_name is not None:
        request_iface = cfg.registry.getUtility(IRouteRequest, name=route_name)

    mapper = getattr(view, '__view_mapper__', DefaultViewMapper)
    mapped_view = mapper()(view)

    info = LayoutInfo(
        name, layout, mapped_view, view, renderer, cfg.__ptah_action__)
    cfg.registry.registerAdapter(
        info, (context, request_iface), ILayout, name)


class LayoutRenderer(object):

    def __init__(self, layout):
        self.layout = layout

    def __call__(self, context, request):
        chain = query_layout_chain(context, request, self.layout)

        if isinstance(request.wrapped_response, HTTPException):
            return request.wrapped_response

        content = text_(request.wrapped_body, 'utf-8')

        for layout, layoutcontext in chain:
            value = layout.view(layoutcontext, request)
            if value is None:
                value = {}

            system = {'view': request.__view__,
                      'renderer_info': layout.renderer,
                      'context': layoutcontext,
                      'request': request,
                      'wrapped_content': content}

            content = layout.renderer.render(value, system, request)

        if isinstance(content, bytes):
            request.response.body = content
        else:
            request.response.text = content
        return request.response


def wrap_layout(layout=''):
    name = '#layout-{0}'.format(layout)

    info = config.DirectiveInfo()
    info.attach(config.Action(wrap_layout_impl, (name, layout)))
    return name


def wrap_layout_impl(cfg, name, layout):
    renderer = cfg.registry.adapters.lookup(
        (IViewClassifier, Interface, Interface), IView, name=name)
    if renderer is None:
        cfg.registry.registerAdapter(
            LayoutRenderer(layout),
            (IViewClassifier, Interface, Interface), IView, name)
