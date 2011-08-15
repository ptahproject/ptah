""" layout implementation """
import sys, logging
from zope import interface
from zope.component import getSiteManager

from memphis import config
from memphis.view.base import BaseView
from memphis.view.formatter import format
from memphis.view.interfaces import ILayout, LayoutNotFound

log = logging.getLogger('memphis.view')


def queryLayout(view, request, context, name=''):
    sm = getSiteManager()

    while context is not None:
        layout = sm.queryMultiAdapter((view, context, request), ILayout, name)

        if layout is not None:
            return layout

        context = getattr(context, '__parent__', None)

    return None


class Layout(BaseView):
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

        self.__parent__ = view.__parent__

    @property
    def __name__(self):
        return self.name

    def update(self):
        pass

    def render(self):
        if self.template is None:
            raise RuntimeError("Can't render layout: %s"%self.name)

        kwargs = self._params or {}
        kwargs.update({'view': self.view,
                       'context': self.view.context,
                       'layout': self,
                       'layoutcontext': self.context,
                       'mainview': self.mainview,
                       'maincontext': self.maincontext,
                       'request': self.request,
                       'template': self.template,
                       'format': format,
                       'nothing': None})

        return self.template(**kwargs)

    def __call__(self, layout=None, view=None, *args, **kw):
        if view is None:
            view = self.view
        self.mainview = view
        self.maincontext = view.context

        layoutview = self.view
        if layout is not None:
            self.view = layout

        self._params = self.update()

        if self.layout is None:
            return self.render()

        if self.name != self.layout:
            layout = queryLayout(
                view, self.request, view.__parent__, name=self.layout)
            if layout is not None:
                return layout(layout=self, view=view, *args, **kw)
        else:
            context = self.context
            if layoutview.context is not context.__parent__:
                context = context.__parent__

            #else:
            #    context = getattr(context.__parent__, '__parent__', None)
            #if context is None:
            #    context = getRoot(self.context)

            layout = queryLayout(self, self.request, context, name=self.layout)
            if layout is not None:
                return layout(view=view, *args, **kw)

        log.warning("Can't find parent layout: '%s'"%self.layout)
        return self.render()


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
        name, context, view, template, parent, klass, layer, configContext, info,
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

