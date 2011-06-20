""" layout implementation """
import sys
from zope import interface
from zope.component import getSiteManager

from memphis import config
from memphis.config.directives import getInfo
from memphis.view.interfaces import ILayout, LayoutNotFound


def queryLayout(view, request, context, name=''):
    sm = getSiteManager()

    while context is not None:
        layout = sm.queryMultiAdapter((view, context, request), ILayout, name)

        if layout is not None:
            return layout

        context = getattr(context, '__parent__', None)

    return None


class Layout(object):
    interface.implements(ILayout)

    __name__ = ''

    template = None
    mainview = None
    maincontext = None
    skipParent = False

    _params = None

    def __init__(self, view, context, request):
        self.view = view
        self.context = context
        self.request = request

        self.__parent__ = view.__parent__

    def update(self):
        pass

    def render(self):
        if self.template is None:
            raise RuntimeError("Can't render layout: %s"%self.__name__)

        kwargs = self._params or {}
        kwargs.update({'view': self.view,
                       'context': self.view.context,
                       'layout': self,
                       'layoutcontext': self.context,
                       'mainview': self.mainview,
                       'maincontext': self.maincontext,
                       'request': self.request,
                       'template': self.template,
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

        if self.__name__ != self.layout:
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

        if not self.skipParent:
            raise LayoutNotFound(self.layout)

        return self.render()


def registerLayout(
    name='', context=None, view=None, template=None, parent='',
    klass=None, layer=interface.Interface, 
    skipParent=False, configContext=config.UNSET, **kwargs):

    frame = sys._getframe(1)

    config.action(
        registerLayoutImpl,
        name, context, view, template, parent,
        klass, layer, skipParent, configContext, getInfo(2),
        __frame = frame,
        discriminator = ('memphis.view:layout', name, context, view, layer),
        actionOrder = (config.moduleNum(frame.f_locals['__name__']), 300),
        **kwargs)


def registerLayoutImpl(
    name='', context=None, view=None, template=None, parent='',
    klass=None, layer=interface.Interface, 
    skipParent=False, configContext=config.UNSET, info='', **kwargs):

    if not parent:
        layout = None
    elif parent == '.':
        layout = ''
    else:
        layout = parent

    # Build a new class
    cdict = {'__name__': name,
             'layout': layout,
             'skipParent': skipParent}
    if template is not None:
        cdict['template'] = template

    cdict.update(kwargs)

    if klass is not None and issubclass(klass, Layout):
        layout_class = klass
        for attr, value in cdict.items():
            setattr(layout_class, attr, value)
    else:
        if klass is None:
            bases = (Layout,)
        else:
            bases = (klass, Layout)

        layout_class = type(str('Layout<%s>'%name), bases, cdict)

    # register layout adapter
    config.registerAdapter(
        layout_class, 
        (view, context, layer), ILayout, name, configContext, info)
