""" layout implementation """
from zope import interface
from pyramid.location import lineage
from pyramid.interfaces import IRequest, IRouteRequest

from ptah import config
from ptah.view.base import View
from ptah.view.interfaces import ILayout
from ptah.view.customize import LayerWrapper


def query_layout(context, request, name=''):
    """ query named layout for context """
    assert IRequest.providedBy(request), u"must pass in a request object"

    for context in lineage(context):
        layout = request.registry.queryMultiAdapter(
            (context, request), ILayout, name)
        if layout is not None:
            return layout

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


class Layout(View):
    interface.implements(ILayout)

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


def register_layout(
    name='', context=None, parent='',
    klass=Layout, template = None, route=None, layer=''):

    if not klass or not issubclass(klass, Layout):
        raise ValueError("klass has to inherit from Layout class")

    discriminator = ('ptah.view:layout', name, context, route, layer)

    info = config.DirectiveInfo()
    info.attach(
        config.Action(
            LayerWrapper(register_layout_impl, discriminator),
            (klass, name, context, template, parent, route),
            discriminator = discriminator)
        )


def register_layout_impl(
    cfg, klass, name, context, template, parent, route_name):

    if not parent:
        layout = None
    elif parent == '.':
        layout = ''
    else:
        layout = parent

    # class attributes
    cdict = {'name': name,
             'layout': layout}

    if template is not None:
        cdict['template'] = template

    if issubclass(klass, Layout) and klass is not Layout:
        layout_class = klass
        for attr, value in cdict.items():
            setattr(layout_class, attr, value)
    else:
        layout_class = type(str('Layout<%s>'%name), (Layout,), cdict)

    layout_class.__config_action__ = cfg.action

    # register layout
    request_iface = IRequest
    if route_name is not None:
        request_iface = cfg.registry.getUtility(
            IRouteRequest, name=route_name)

    cfg.registry.registerAdapter(
        layout_class, (context, request_iface), ILayout, name)
