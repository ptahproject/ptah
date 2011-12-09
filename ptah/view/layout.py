""" layout implementation """
from zope.interface import implementer, providedBy, Interface
from pyramid.compat import text_type
from pyramid.location import lineage
from pyramid.interfaces import IView, IRequest, IRouteRequest
from pyramid.interfaces import IViewClassifier

from ptah import config
from ptah.view.base import View
from ptah.view.interfaces import ILayout

LAYOUT_ID = 'ptah.view:layout'


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
            return layout_factory(context, request)

    return None


def query_layout_chain(context, request, layoutname=''):
    chain = []

    layout = query_layout(context, request, layoutname)
    if layout is None:
        return chain

    chain.append(layout)
    contexts = {layoutname: layout.context}

    while layout is not None:
        if layout.layout in contexts:
            l_context = contexts[layout.layout].__parent__
        else:
            l_context = context

        layout = query_layout(l_context, request, layout.layout)
        if layout is not None:
            chain.append(layout)
            contexts[layout.name] = layout.context

            if layout.layout is None:
                break

    return chain


class LayoutRenderer(object):

    def __init__(self, layout):
        self.layout = layout

    def __call__(self, context, request, content):
        chain = query_layout_chain(context, request, self.layout)

        for layout in chain:
            layout.update()
            content = layout.render(content)

        return content


@implementer(ILayout)
class Layout(View):
    """ Layout """

    name = ''
    template = None

    @property
    def __name__(self):
        return self.name

    def render(self, content, **kwargs):
        if self.template is None:
            return content

        kwargs.update({'view': self,
                       'content': content,
                       'context': self.context,
                       'request': self.request})

        return self.template(**kwargs)


def layout(name='', context=None, parent='',
           template = None, route=None, layer=''):
    info = config.DirectiveInfo()

    def wrapper(cls):
        discr = (LAYOUT_ID, name, context, route, layer)

        intr = config.Introspectable(LAYOUT_ID, discr, name, LAYOUT_ID)
        intr['name'] = name
        intr['context'] = context
        intr['layer'] = layer
        intr['route'] = route
        intr['parent'] = parent
        intr['codeinfo'] = info.codeinfo

        info.attach(
            config.Action(
                config.LayerWrapper(register_layout_impl, discr),
                (cls, name, context, template, parent, route, intr),
                discriminator=discr, introspectables=(intr,))
            )
        return cls

    return wrapper


def register_layout(
    name='', context=None, parent='',
    cls = Layout, template = None, route=None, layer=''):

    if not cls or not issubclass(cls, Layout):
        raise ValueError("klass has to inherit from Layout class")

    discr = (LAYOUT_ID, name, context, route, layer)

    intr = config.Introspectable(LAYOUT_ID, discr, name, LAYOUT_ID)
    intr['name'] = name
    intr['context'] = context
    intr['layer'] = layer
    intr['route'] = route
    intr['parent'] = parent

    info = config.DirectiveInfo()
    info.attach(
        config.Action(
            config.LayerWrapper(register_layout_impl, discr),
            (cls, name, context, template, parent, route, intr),
            discriminator=discr, introspectables=(intr,) )
        )


def register_layout_impl(
    cfg, klass, name, context, template, parent, route_name, intr):

    if not parent:
        layout = None
    elif parent == '.':
        layout = ''
    else:
        layout = parent

    # class attributes
    cdict = {'name': name,
             'layout': layout,
             '__config_action__': cfg.__ptah_action__}

    if template is not None:
        cdict['template'] = template

    if issubclass(klass, Layout) or klass is Layout:
        bases = (klass,)
    else:
        bases = (klass, Layout)

    layout_class = type(str('Layout<%s>'%name), bases, cdict)

    # register layout
    request_iface = IRequest
    if route_name is not None:
        request_iface = cfg.registry.getUtility(
            IRouteRequest, name=route_name)

    intr['class'] = layout_class

    cfg.registry.registerAdapter(
        layout_class, (context, request_iface), ILayout, name)


import random, string

LAYOUT_WRAPPER_ID = 'ptah.view:layout-wrapper'


class LayoutWrapperRenderer(object):

    def __init__(self, layout):
        self.layout = layout

    def __call__(self, context, request):
        chain = query_layout_chain(context, request, self.layout)

        content = request.wrapped_body

        for layout in chain:
            layout.update()
            content = layout.render(content)

        response = request.response
        if type(content) is text_type:
            response.unicode_body = content
        else:
            response.body = content

        return response


def layout_wrapper(layout='', route=''):
    info = config.DirectiveInfo()

    name = 'layout-{0}'.format(
        ''.join(random.choice(string.ascii_lowercase) for x in range(20)))

    discr = (LAYOUT_WRAPPER_ID, name)
    wrapper = LayoutWrapperRenderer(layout)

    info.attach(
        config.Action(
            layout_wrapper_impl, (name, wrapper, route), discriminator=discr)
        )
    return name


def layout_wrapper_impl(config, name, wrapper, route_name):
    registry = config.registry

    request_iface = IRequest
    if route_name:
        request_iface = registry.getUtility(IRouteRequest, name=route_name)

    registry.registerAdapter(
        wrapper,
        (IViewClassifier, request_iface, Interface), IView, name)
