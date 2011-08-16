""" layout implementation """
import sys, logging
from zope import interface
from zope.component import getSiteManager

from memphis import config
from memphis.view.base import View
from memphis.view.formatter import format
from memphis.view.interfaces import ILayout

log = logging.getLogger('memphis.view')


def queryLayout(view, request, context, name=''):
    sm = getSiteManager()

    while context is not None:
        layout = sm.queryMultiAdapter((view, context, request), ILayout, name)
        if layout is not None:
            return layout

        context = getattr(context, '__parent__', None)

    return None


class Layout(View):
    interface.implements(ILayout)

    name = ''
    template = None
    mainview = None
    maincontext = None

    _params = None

    def __init__(self, view, context, request):
        self.view = view
        self.context = context
        self.request = request
        self.__parent__ = getattr(view, '__parent__', context)

    @property
    def __name__(self):
        return self.name

    def render(self, content):
        if self.template is None:
            return content

        kwargs = self._params or {}
        kwargs.update({'view': self,
                       'content': content,
                       'context': self.context,
                       'request': self.request,
                       'format': format})

        return self.template(**kwargs)

    def __call__(self, content, layout=None, view=None, *args, **kw):
        if view is None:
            view = self.view
        if view is not None:
            self.mainview = view
            self.maincontext = view.context

        layoutview = self.view
        if layout is not None:
            self.view = layout

        self._params = self.update()

        result = self.render(content)

        if self.layout is None:
            return result

        if self.name != self.layout:
            layout = queryLayout(
                view, self.request, view.__parent__, self.layout)
            if layout is not None:
                return layout(result, layout=self, view=view, *args, **kw)
        else:
            context = self.context
            if layoutview.context is not context.__parent__:
                context = context.__parent__

            #else:
            #    context = getattr(context.__parent__, '__parent__', None)
            #if context is None:
            #    context = getRoot(self.context)

            layout = queryLayout(self, self.request, context, self.layout)
            if layout is not None:
                return layout(result, view=view, *args, **kw)

        log.warning("Can't find parent layout: '%s'"%self.layout)
        return self.render(result)


def registerLayout(
    name='', context=None, view=None, template=None, parent='',
    klass=Layout, layer=interface.Interface, configContext=config.UNSET, **kw):

    if not klass or not issubclass(klass, Layout):
        raise ValueError("klass has to inherit from Layout class")

    frame = sys._getframe(1)
    info = config.getInfo(2)
    _locals = config.getModule(frame)

    config.action(
        registerLayoutImpl,
        name,context,view,template,parent,klass,layer,configContext,info,
        __frame = frame,
        __info = info,
        __discriminator = ('memphis.view:layout', name, context, view, layer),
        __order = (config.moduleNum(_locals['__name__']), 300),
        **kw)


def registerLayoutImpl(
    name, context, view, template, parent,
    klass, layer, configContext, info, **kwargs):

    if klass in _registered:
        raise ValueError("Class can't be reused for different layouts")

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

    cdict.update(kwargs)

    if issubclass(klass, Layout) and klass is not Layout:
        layout_class = klass
        _registered.append(klass)
        for attr, value in cdict.items():
            setattr(layout_class, attr, value)
    else:
        layout_class = type(str('Layout<%s>'%name), (Layout,), cdict)

    # register layout adapter
    config.registerAdapter(
        layout_class, 
        (view, context, layer), ILayout, name, configContext, info)


_registered = []

@config.cleanup
def cleanUp():
    _registered[:] = []

