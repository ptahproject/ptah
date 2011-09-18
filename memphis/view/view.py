""" view implementation """
import sys, inspect
from zope import interface
from zope.interface import providedBy
from zope.component import queryUtility, getSiteManager

from pyramid.config.views import requestonly, isexception
from pyramid.interfaces import IView
from pyramid.interfaces import IRequest
from pyramid.interfaces import IRouteRequest
from pyramid.interfaces import IViewClassifier
from pyramid.interfaces import IExceptionViewClassifier
from pyramid.interfaces import IAuthorizationPolicy
from pyramid.interfaces import IAuthenticationPolicy
from pyramid.httpexceptions import HTTPForbidden

from memphis import config
from memphis.view.base import View
from memphis.view.customize import LayerWrapper
from memphis.view.renderers import Renderer, SimpleRenderer


def renderView(name, context, request):
    adapters = getSiteManager().adapters

    view_callable = adapters.lookup(
        (IViewClassifier, providedBy(request), providedBy(context)),
        IView, name=name, default=None)

    return view_callable(context, request)


chained = object()

def subpathWrapper(factory, renderer, subpaths):

    def wrapper(context, request):
        if request.subpath:
            item = request.subpath[0]
            if item in subpaths:
                render, meth = subpaths[item]

                def viewFactory(context, request):
                    view = factory(context, request)
                    return view, meth(view)

                request.subpath = tuple(request.subpath[1:])
                result = render(context, request, viewFactory)
                if result is not chained:
                    return result

        return renderer(context, request)

    return wrapper


class subpath(object):

    def __init__(self, meth=None, name='', renderer=None):
        self.name = name
        self.renderer = renderer
        if meth is not None:
            frame = sys._getframe(1)
            try:
                self(meth, frame)
                frame.f_locals[meth.__name__] = meth
            finally:
                del frame

    def __call__(self, method, frame=None):
        if frame is None:
            frame = sys._getframe(1)

        if '__module__' not in frame.f_locals:
            del frame
            raise ValueError(
                "Can apply 'subpath' decorator only to class methods")

        subpaths = frame.f_locals.get('__subpath_traverse__', None)
        if subpaths is None:
            subpaths = {}
            frame.f_locals['__subpath_traverse__'] = subpaths
        del frame

        renderer = self.renderer
        if renderer:
            render = renderer
        else:
            def render(context, request, factory):
                return factory(context, request)[1]

        if self.name:
            subpaths[self.name] = render, method
        else:
            subpaths[method.__name__] = render, method

        return method


def registerView(
    name='', factory=View, context=None, renderer=None, template=None,
    route=None, layout='', permission='__no_permission_required__',
    default=False, decorator=None, layer=''):

    if renderer is not None and template is not None:
        raise ValueError("renderer and template can't be used at the same time.")

    if factory is None or not callable(factory):
        raise ValueError('view factory is required')

    discriminator = ('memphis.view:view', name, context, route, layer)

    info = config.DirectiveInfo()
    info.attach(
        config.Action(
            LayerWrapper(registerViewImpl, discriminator),
            (factory, name, context, renderer, template,
             route, layout, permission, default, decorator),
            discriminator = discriminator)
        )


AUTH = None
AUTHZ = None

@config.handler(config.SettingsInitialized)
def initialized(ev):
    global AUTH, AUTHZ

    sm = getSiteManager()
    AUTH = sm.queryUtility(IAuthenticationPolicy)
    AUTHZ = sm.queryUtility(IAuthorizationPolicy)


def registerViewImpl(
    factory, name, context, renderer, template, route_name, layout,
    permission, default, decorator):

    if renderer is None:
        if template is not None:
            renderer = Renderer(template, layout=layout).bind(
                viewMapper(factory, 'update'))
        else:
            renderer = SimpleRenderer(layout=layout).bind(
                viewMapper(factory, 'render'))

    # add 'subpath' support
    if inspect.isclass(factory):
        subpath_traverse = getattr(factory, '__subpath_traverse__', None)
        if subpath_traverse is not None:
            renderer = subpathWrapper(
                viewInstanceMapper(factory), renderer, subpath_traverse)

    # decorate renderer
    if decorator:
        renderer = decorator(renderer)

    # build pyramid view
    if permission == '__no_permission_required__':
        permission = None

    sm = getSiteManager()

    auth = sm.queryUtility(IAuthenticationPolicy)
    authz = sm.queryUtility(IAuthorizationPolicy)
    if permission:
        def pyramidView(context, request):
            principals = AUTH.effective_principals(request)
            if AUTHZ.permits(context, principals, permission):
                return renderer(context, request)

            msg = getattr(request, 'authdebug_message',
                          'Unauthorized: %s failed permission check'%factory)
            raise HTTPForbidden(msg)
    else:
        pyramidView = renderer

    # register view
    if context is None:
        context = interface.Interface

    if isexception(context):
        view_classifier = IExceptionViewClassifier
    else:
        view_classifier = IViewClassifier

    request_iface = IRequest
    if route_name is not None:
        request_iface = sm.getUtility(IRouteRequest, name=route_name)

    sm.registerAdapter(
        pyramidView, (view_classifier, request_iface, context), IView, name)

    if default:
        registerDefaultViewImpl(name, context, request_iface, pyramidView)


def registerDefaultView(name, context=interface.Interface, request=IRequest):
    info = config.DirectiveInfo()
    info.attach(
        config.Action(
            registerDefaultViewImpl,
            (name, context, request),
            discriminator = ('memphis.view:defaultView', name, context)))


def registerDefaultViewImpl(
    name, context=interface.Interface, request_iface=IRequest, view=None):
    if view is None:
        def view(context, request):
            return renderView(name, context, request)

    getSiteManager().registerAdapter(
        view, (IViewClassifier, request_iface, context), IView, '')


def viewMapper(view, attr=None):
    if inspect.isclass(view):
        ronly = requestonly(view, attr)
        attr = attr or '__call__'
        meth = getattr(view, attr)
        if attr != 'update':
            update = getattr(view, 'update', None)
        else:
            update = None
        updateClass = callable(update)

        if ronly:
            def _class_request_view(context, request):
                inst = view(request)
                if updateClass:
                    update(inst)
                return inst, meth(inst)
            return _class_request_view
        else:
            def _class_view(context, request):
                inst = view(context, request)
                if updateClass:
                    update(inst)
                return inst, meth(inst)
            return _class_view
    else:
        ronly = requestonly(view)
        if ronly:
            def _request_view(context, request):
                return None, view(request)
            return _request_view
        else:
            def _view(context, request):
                return None, view(context, request)
            return _view


def viewInstanceMapper(view):
    ronly = requestonly(view)
    if ronly:
        def _class_requestonly_view(context, request):
            return view(request)
        return _class_requestonly_view
    else:
        def _class_view(context, request):
            return view(context, request)
        return _class_view
