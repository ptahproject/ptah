""" layout implementation """
import sys, logging
from zope import interface
from pyramid.interfaces import IRequest, IRouteRequest

from memphis import config
from memphis.view.base import View
from memphis.view.formatter import format
from memphis.view.interfaces import ILayout
from memphis.view.customize import LayerWrapper

log = logging.getLogger('memphis.view')


def query_layout(request, context, name=''):
    """ query named layout for context """
    assert IRequest.providedBy(request), u"must pass in a request object"

    while context is not None:
        layout = config.registry.queryMultiAdapter(
            (context, request), ILayout, name)
        if layout is not None:
            return layout

        context = getattr(context, '__parent__', None)

    return None


class Layout(View):
    interface.implements(ILayout)

    name = ''
    template = None
    view = None
    viewcontext = None

    @property
    def __name__(self):
        return self.name

    def render(self, content, **kwargs):
        if self.template is None:
            return content

        kwargs.update({'view': self,
                       'content': content,
                       'context': self.context,
                       'request': self.request,
                       'format': format})

        return self.template(**kwargs)

    def __call__(self, content, layout=None, view=None):
        if view is not None:
            self.view = view
            self.viewcontext = getattr(view, 'context', self.context)
        if layout is not None:
            self.view = layout.view or self.view
            self.viewcontext = layout.viewcontext or self.viewcontext

        result = self.render(content, **(self.update() or {}))
        if self.layout is None:
            return result

        parent = getattr(view, '__parent__', self.context)

        if self.name != self.layout:
            layout = query_layout(self.request, parent, self.layout)
            if layout is not None:
                return layout(result, layout=self, view=view)
        else:
            if layout is not None: # pragma: no cover
                context = layout.context
            else:
                context = self.context
            parent = getattr(context, '__parent__', None)
            if parent is not None:
                layout = query_layout(self.request, parent, self.layout)
                if layout is not None:
                    return layout(result, view=view)

        log.warning("Can't find parent layout: '%s'"%self.layout)
        return self.render(result)


def register_layout(
    name='', context=None, parent='',
    klass=Layout, template = None, route=None, layer=''):

    if not klass or not issubclass(klass, Layout):
        raise ValueError("klass has to inherit from Layout class")

    discriminator = ('memphis.view:layout', name, context, route, layer)

    info = config.DirectiveInfo()
    info.attach(
        config.Action(
            LayerWrapper(register_layout_impl, discriminator),
            (klass, name, context, template, parent, route),
            discriminator = discriminator)
        )


def register_layout_impl(config, klass, name, context, template, parent, route_name):
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

    # register layout
    request_iface = IRequest
    if route_name is not None:
        request_iface = config.registry.getUtility(
            IRouteRequest, name=route_name)

    config.registry.registerAdapter(
        layout_class, (context, request_iface), ILayout, name)
