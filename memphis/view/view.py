""" view implementation """
import sys, inspect
from zope import interface
from zope.interface import providedBy
from zope.component import queryUtility, getSiteManager

from webob.exc import HTTPForbidden

from pyramid.config import requestonly
from pyramid.interfaces import IView
from pyramid.interfaces import IRequest
from pyramid.interfaces import IViewClassifier
from pyramid.interfaces import IAuthenticationPolicy

from memphis import config
from memphis.view.base import View
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
    name, factory=View, context=None, template=None,
    layer=IRequest, layout='', permission='__no_permission_required__',
    default=False, decorator=None):

    if factory is None or not callable(factory):
        raise ValueError('view factory is required')

    info = config.DirectiveInfo()
    info.attach(
        config.Action(
            registerViewImpl,
            (factory, name, context, template,
             layer, layout, permission, default, decorator),
            discriminator = ('memphis.view:view', name, context, layer)))


def registerViewImpl(
    factory, name, context, template, layer, layout, 
    permission, default, decorator):

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
    if auth and permission:
        def pyramidView(context, request):
            principals = auth.effective_principals(request)
            if auth.permits(context, principals, permission):
                return renderer(context, request)

            msg = getattr(request, 'authdebug_message',
                          'Unauthorized: %s failed permission check'%factory)
            raise HTTPForbidden(msg)
    else:
        pyramidView = renderer

    # register view
    if context is None:
        context = interface.Interface

    sm.registerAdapter(
        pyramidView, (IViewClassifier, layer, context), IView, name)

    if default:
        registerDefaultViewImpl(name, context, layer)


def registerDefaultView(name, context=interface.Interface, layer=IRequest):
    info = config.DirectiveInfo()
    info.attach(
        config.Action(
            registerDefaultViewImpl,
            (name, context, layer),
            discriminator = ('memphis.view:defaultView', name, context, layer)))


def registerDefaultViewImpl(name, context=interface.Interface, layer=IRequest):
    def view(context, request):
        return renderView(name, context, request)

    getSiteManager().registerAdapter(
        view, (IViewClassifier, layer, context), IView, '')


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
