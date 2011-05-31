""" view implementation """
from zope import interface, component
from zope.interface import providedBy
from zope.component import getSiteManager

from webob.exc import HTTPException

from pyramid.response import Response
from pyramid.interfaces import IRequest, IView, IViewClassifier

from memphis import config
from memphis.view.layout import queryLayout
from memphis.view.interfaces import IDefaultView


class View(object):
    interface.implements(IView)

    __name__ = ''
    template = None
    layoutname = ''
    isRedirected = False
    renderParams = None

    content_type = 'text/html'

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def __parent__(self):
        return self.context

    def update(self):
        pass

    def render(self):
        kwargs = self.renderParams or {}
        kwargs.update({'view': self,
                       'context': self.context,
                       'request': self.request,
                       'template': self.template,
                       'nothing': None})

        return self.template(**kwargs)

    def __call__(self, *args, **kw):
        try:
            self.renderParams = self.update()

            layout = queryLayout(
                self, self.request, self.__parent__, self.layoutname)
            if layout is None:
                res = self.render()
            else:
                res = layout()

            return Response(body=res, status=200,
                            content_type = self.content_type)
        except HTTPException, response:
            return response


class DefaultView(object):
    interface.implements(IDefaultView)

    def __init__(self, name):
        self.name = name

    def __call__(self, context, request):
        return self.name


def renderView(name, context, request):
    adapters = getSiteManager().adapters

    view_callable = adapters.lookup(
        (IViewClassifier, providedBy(request), providedBy(context)),
        IView, name=name, default=None)

    return view_callable(context, request)


class PyramidView(object):

    def __init__(self, factory, permission):
        self.factory = factory
        self.permission = permission

    def view(self, context, request):
        """ i use this for testing only """
        return self.factory(context, request)

    def __call__(self, context, request):
        # fixme: add security checks here

        return self.factory(context, request)()


class DefaultPyramidView(object):

    def __init__(self, name):
        self.name = name

    def __call__(self, context, request):
        return renderView(self.name, context, request)


_registered = []

@config.cleanup
def cleanUp():
    _registered[:] = []


def registerView(
    name='', context=None, klass=None, template=None,
    layer=IRequest, layout='', permission='', configContext=None, info=''):

    if klass is not None and klass in _registered:
        raise ValueError("Class can be used for view only once.")

    cdict = {'__name__': name,
             'layoutname': layout,
             'template': template}

    if context is None:
        context = interface.Interface

    if klass is not None and issubclass(klass, View):
        _registered.append(klass)
        view_class = klass
        for attr, value in cdict.items():
            setattr(view_class, attr, value)
    else:
        # Build a new class
        if klass is None:
            bases = (View, )
        else:
            bases = (klass, View)

        view_class = type('View %s'%klass, bases, cdict)

    config.registerAdapter(
        PyramidView(view_class, permission),
        (IViewClassifier, layer, context), IView, name,
        configContext, info)


def registerDefaultView(name, context=interface.Interface,
                        layer=IRequest, configContext = None):
    config.registerAdapter(
        DefaultView(name), (context, layer), IDefaultView, '', configContext)

    config.registerAdapter(
        DefaultPyramidView(name),
        (IViewClassifier, layer, context), IView, '', configContext)
