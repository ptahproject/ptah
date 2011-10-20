""" view implementation """
import sys, inspect
from zope import interface
from zope.interface import providedBy

from pyramid.response import Response
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.httpexceptions import WSGIHTTPException
from pyramid.config.views import requestonly, isexception
from pyramid.interfaces import IView
from pyramid.interfaces import IRequest
from pyramid.interfaces import IRouteRequest
from pyramid.interfaces import IViewClassifier
from pyramid.interfaces import IExceptionViewClassifier

from ptah import config
from ptah.view.base import View
from ptah.view.customize import LayerWrapper
from ptah.view.renderers import \
    PermissionRenderer, ViewRenderer, TemplateRenderer, LayoutRenderer


def render_view(name, context, request):
    adapters = config.registry.adapters

    view_callable = adapters.lookup(
        (IViewClassifier, providedBy(request), providedBy(context)),
        IView, name=name, default=None)

    return view_callable(context, request)


class PyramidView(object):

    def __init__(self, chain):
        self.renderers = chain
    
    def __call__(self, context, request):
        content = None

        try:
            for renderer in self.renderers:
                content = renderer(context, request, content)
        except WSGIHTTPException, resp:
            return resp

        if isinstance(content, Response):
            return content

        response = request.response
        if type(content) is unicode:
            response.unicode_body = content
        else:
            response.body = content

        return response


chained = object()

def subpath_wrapper(factory, renderer, subpaths):

    def wrapper(context, request, content):
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

        return renderer(context, request, content)

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
            def render(context, request, content):
                return factory(context, request, content)

        if self.name:
            subpaths[self.name] = render, method
        else:
            subpaths[method.__name__] = render, method

        return method


unset = object()

def register_view(
    name=u'', factory=View, context=None, template=None, route=None,
    layout=unset, permission=NO_PERMISSION_REQUIRED, layer=''):

    if factory is None or not callable(factory):
        raise ValueError('view factory is required')

    discriminator = ('ptah.view:view', name, context, route, layer)

    info = config.DirectiveInfo()
    info.attach(
        config.Action(
            LayerWrapper(register_view_impl, discriminator),
            (factory, name, context, template, route, layout, permission),
            discriminator = discriminator)
        )


def register_view_impl(config, factory, name, context, template, route_name,
                       layout, permission):
    chain = []

    # permission
    if permission != NO_PERMISSION_REQUIRED and permission is not None:
        chain.append(PermissionRenderer(permission, factory))

    # view
    if template is None:
        render = ViewRenderer(viewMapper(factory, 'render'))
    else:
        render = TemplateRenderer(viewMapper(factory, 'update'), template)

    # add 'subpath' support
    if inspect.isclass(factory):
        subpath_traverse = getattr(factory, '__subpath_traverse__', None)
        if subpath_traverse is not None:
            render = subpath_wrapper(
                viewInstanceMapper(factory), render, subpath_traverse)
    chain.append(render)

    # layout
    if layout is unset:
        layout = None
        try:
            if issubclass(factory, View):
                layout = ''
        except:
            pass
        
    if layout is not None:
        chain.append(LayoutRenderer(layout))

    # register view
    if isexception(context):
        view_classifier = IExceptionViewClassifier
    else:
        view_classifier = IViewClassifier

    sm = config.registry

    request_iface = IRequest
    if route_name is not None:
        request_iface = sm.getUtility(IRouteRequest, name=route_name)

    sm.registerAdapter(
        PyramidView(chain),
        (view_classifier, request_iface, context or interface.Interface),
        IView, name)


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
