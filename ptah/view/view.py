""" view implementation """
import inspect
from zope import interface
from zope.interface import providedBy

from pyramid.response import Response
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.httpexceptions import WSGIHTTPException
from pyramid.config.views import requestonly, isexception
from pyramid.interfaces import IView
from pyramid.interfaces import IRequest, IRouteRequest
from pyramid.interfaces import IViewClassifier, IExceptionViewClassifier

from ptah import config
from ptah.view.base import View
from ptah.view.customize import LayerWrapper
from ptah.view.layout import LayoutRenderer
from ptah.view.renderers import \
     PermissionRenderer, ViewRenderer, TemplateRenderer


def render_view(name, context, request):
    adapters = request.registry.adapters

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
                if isinstance(content, Response):
                    return content
        except WSGIHTTPException, resp:
            return resp

        response = request.response
        if type(content) is unicode:
            response.unicode_body = content
        else:
            response.body = content

        return response


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


def register_view_impl(cfg, factory, name, context, template, route_name,
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
    factory.__view_renderer__ = render

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

    sm = cfg.registry

    request_iface = IRequest
    if route_name is not None:
        request_iface = sm.getUtility(IRouteRequest, name=route_name)

    pview = PyramidView(chain)
    factory.__renderer__ = pview
    pview.__config_action__ = cfg.action

    sm.registerAdapter(
        pview,
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
