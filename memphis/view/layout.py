"""

$Id: layout.py 11635 2011-01-18 07:03:08Z fafhrd91 $
"""
from zope import interface, component
from pyramid.interfaces import IRequest

from memphis import config
from memphis.view.interfaces import ILayout, LayoutNotFound


def queryLayout(view, request, context, name=''):
    sm = component.getSiteManager()

    while context is not None:
        layout = sm.queryMultiAdapter((view, context, request), ILayout, name)

        if layout is not None:
            return layout

        context = getattr(context, '__parent__', None)

    return None


class Layout(object):
    interface.implements(ILayout)

    template = None
    mainview = None
    maincontext = None

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

        kwargs = {'view': self.view,
                  'context': self.view.context,
                  'layout': self,
                  'layoutcontext': self.context,
                  'mainview': self.mainview,
                  'maincontext': self.maincontext,
                  'request': self.request,
                  'template': self.template,
                  'nothing': None}

        return self.template(**kwargs)

    def __call__(self, layout=None, view=None, *args, **kw):
        if view is None:
            view = self.view
        self.mainview = view
        self.maincontext = view.context

        layoutview = self.view
        if layout is not None:
            self.view = layout

        self.update()

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

        raise LayoutNotFound(self.layout)


def registerLayout(
    name='', context=None, view=None, template=None, parent='',
    klass=None, layer=IRequest, configContext=None, **kwargs):

    if not parent:
        layout = None
    elif parent == '.':
        layout = ''
    else:
        layout = parent

    # Build a new class
    cdict = {'__name__': name,
             'layout': layout,
             'template': template}
    cdict.update(kwargs)

    if klass is None:
        bases = (Layout,)
    else:
        bases = (klass, Layout)

    newclass = type(str('Layout<%s>'%name), bases, cdict)

    # register layout
    config.registerAdapter(
        newclass, (view, context, layer), ILayout, name, configContext)
