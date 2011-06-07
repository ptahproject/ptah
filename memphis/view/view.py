""" view implementation """
import sys
from zope import interface, component
from zope.interface import providedBy
from zope.component import getSiteManager

from webob.exc import HTTPException

from pyramid.response import Response
from pyramid.exceptions import Forbidden
from pyramid.interfaces import IRequest, IView, IViewClassifier
from pyramid.interfaces import IAuthenticationPolicy

from memphis import config
from memphis.config.directives import getInfo

from memphis.view.layout import queryLayout
from memphis.view.interfaces import IDefaultView


class View(object):
    interface.implements(IView)

    __name__ = ''
    template = None
    layoutname = ''
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

    def __init__(self, factory):
        self.factory = factory

    def view(self, context, request):
        """ i use this for testing only """
        return self.factory(context, request)

    def __call__(self, context, request):
        return self.factory(context, request)()


class SecuredPyramidView(PyramidView):

    def __init__(self, factory, auth, permission):
        self.factory = factory
        self.auth = auth
        self.permission = permission

    def __call__(self, context, request):
        principals = self.auth.effective_principals(request)
        if self.auth.permits(context, principals, self.permission):
            return self.factory(context, request)()
        msg = getattr(request, 'authdebug_message',
                      'Unauthorized: %s failed permission check' % self.factory)
        raise Forbidden(msg)


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
    layer=IRequest, layout='', permission='', configContext=None):
    
    config.action(
        registerViewImpl,
        name, context, klass, template, 
        layer, layout, permission, configContext, getInfo(),
        __frame = sys._getframe(1))


def registerViewImpl(
    name='', context=None, klass=None, template=None,
    layer=IRequest, layout='', permission='', configContext=None, info=''):

    if permission == '__no_permission_required__':
        permission = None

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

    auth = getSiteManager().queryUtility(IAuthenticationPolicy)
    if auth and permission:
        view = SecuredPyramidView(view_class, auth, permission)
    else:
        view = PyramidView(view_class)

    config.registerAdapter(
        view,
        (IViewClassifier, layer, context), IView, name,
        configContext, info)


def registerDefaultView(name, context=interface.Interface,
                        layer=IRequest, configContext = None):

    config.action(
        registerDefaultViewImpl, name, context, layer, 
        configContext, getInfo(),
        __frame = sys._getframe(1))


def registerDefaultViewImpl(name, context=interface.Interface,
                            layer=IRequest, configContext = None, info=''):
    config.registerAdapter(
        DefaultView(name), 
        (context, layer), 
        IDefaultView, '', configContext, info)

    config.registerAdapter(
        DefaultPyramidView(name),
        (IViewClassifier, layer, context), IView, '', configContext, info)
