""" view implementation """
import simplejson, sys
from zope import interface
from zope.interface import providedBy
from zope.component import getSiteManager

from webob import Response
from webob.exc import HTTPException, HTTPNotFound, HTTPForbidden
from pyramid.interfaces import IView
from pyramid.interfaces import IRequest
from pyramid.interfaces import IViewClassifier
from pyramid.interfaces import IAuthenticationPolicy

from memphis import config
from memphis.view.base import View
from memphis.view.directives import pyramidView
from memphis.view.tmpl import path
from memphis.view.layout import queryLayout
from memphis.view.interfaces import IRenderer


def renderView(name, context, request):
    adapters = getSiteManager().adapters

    view_callable = adapters.lookup(
        (IViewClassifier, providedBy(request), providedBy(context)),
        IView, name=name, default=None)

    return view_callable(context, request)


class SimpleRenderer(object):
    interface.implements(IRenderer)

    layout = ''
    content_type = 'text/html'

    def __init__(self, layout='', content_type='text/html'):
        self.content_type = content_type
        self.layout = layout

    def __call__(self, context, request, view=None, result=''):
        response = request.response
        response.content_type = self.content_type

        if self.layout is not None:
            layout = queryLayout(
                view, request, context, self.layout)
            if layout is not None:
                result = layout(result)

        if type(result) is unicode:
            response.unicode_body = result
        else:
            response.body = result

        return response


class Renderer(object):
    interface.implements(IRenderer)

    layout = ''
    content_type = 'text/html'
    template = None

    def __init__(self, template=None, layout='', content_type='text/html'):
        if template is None:
            raise ValueError("template is required")

        self.template = template
        self.content_type = content_type
        self.layout = layout

    def __call__(self, context, request, view=None, params=None):
        response = request.response
        response.content_type = self.content_type

        kwargs = {'view': view,
                  'context': context,
                  'request': request,
                  'format': format}
        if params:
            kwargs.update(params)

        result = self.template(**kwargs)

        if self.layout is not None:
            layout = queryLayout(
                view, request, context, self.layout)
            if layout is not None:
                result = layout(result)

        if type(result) is unicode:
            response.unicode_body = result
        else:
            response.body = result

        return response


class JSONRenderer(object):
    interface.implements(IRenderer)

    content_type = 'text/json'

    @classmethod
    def render(cls, context, request, view, result, dumps=simplejson.dumps):
        response = request.response
        response.content_type = cls.content_type
        response.body = dumps(result)
        return response


json = JSONRenderer.render


def registerView(
    name, factory=View, context=None, template=None,
    layer = IRequest, layout='', permission='__no_permission_required__',
    default=False, decorator=None, configContext=config.UNSET):

    if factory is None or not callable(factory):
        raise ValueError('view factory is required')

    info = config.getInfo(2)

    config.action(
        registerViewImpl,
        name, factory, context, template,
        layer, layout, permission, default, decorator, configContext, info,
        __info = info,
        __frame = sys._getframe(1),
        __discriminator = ('memphis.view:view', name, context, layer))


def registerViewImpl(
    name, factory, context, template, layer, layout, permission, 
    default, decorator, configContext=config.UNSET, info=''):

    renderer = factory

    if template is not None:
        tmpl_renderer = Renderer(template, layout=layout)
        if type(factory) is type:
            def renderer(context, request):
                view = factory(context, request)
                view.__name__ = name
                view.__parent__ = context
                return tmpl_renderer(context, request, view, view.update())
        else:
            def renderer(context, request):
                result = factory(context, request)
                return tmpl_renderer(context, request, None, result)
    else:
        render = SimpleRenderer(layout=layout)
        if type(factory) is type:
            def renderer(context, request):
                view = factory(context, request)
                view.__name__ = name
                view.__parent__ = context
                view.update()
                return render(context, request, view, view.render())
        else:
            def renderer(context, request):
                result = factory(context, request)
                return render(context, request, None, result)

    # add 'subpath' support
    subpath_traverse = getattr(factory, '__subpath_traverse__', None)
    if subpath_traverse is not None:
        renderer = subpathWrapper(factory, renderer, subpath_traverse)

    # decorate renderer
    if decorator:
        renderer = decorator(renderer)

    # build pyramid view
    if permission == '__no_permission_required__':
        permission = None

    auth = getSiteManager().queryUtility(IAuthenticationPolicy)
    if auth and permission:
        def pyramidView(context, request):
            principals = auth.effective_principals(request)
            if auth.permits(context, principals, permission):
                try:
                    return renderer(context, request)
                except HTTPException, exc:
                    return exc
            msg = getattr(request, 'authdebug_message',
                          'Unauthorized: %s failed permission check'%factory)
            raise HTTPForbidden(msg)
    else:
        def pyramidView(context, request):
            try:
                return renderer(context, request)
            except HTTPException, exc:
                return exc

    # register view
    if context is None:
        context = interface.Interface

    config.registerAdapter(
        pyramidView,
        (IViewClassifier, layer, context), IView, name, configContext, info)

    if default:
        registerDefaultViewImpl(name, context, layer, configContext, info)


def registerDefaultView(name, context=interface.Interface,
                        layer=IRequest, configContext = config.UNSET):

    config.action(
        registerDefaultViewImpl, name, context, layer, 
        configContext, 
        __info = getInfo(2),
        __frame = sys._getframe(1))


def registerDefaultViewImpl(
    name, context=interface.Interface,
    layer=IRequest, configContext = config.UNSET, info=''):

    def view(context, request):
        return renderView(name, context, request)

    config.registerAdapter(
        view,
        (IViewClassifier, layer, context), IView, '', configContext, info)


def subpathWrapper(factory, renderer, subpaths):

    def wrapper(context, request):
        if request.subpath:
            item = request.subpath[0]
            if item in subpaths:
                meth = subpaths[item]
                request.subpath = tuple(request.subpath[1:])
                return meth(factory(context, request))

        return renderer(context, request)

    return wrapper


class subpath:

    def __init__(self, name='', renderer=None, decorator=None):
        self.name = name
        self.renderer = renderer
        self.decorator = decorator

    def __call__(self, ob):
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

        if self.decorator:
            method = decorator(ob)
        else:
            method = ob

        if self.renderer:
            def renderSubpath(view):
                return self.renderer(
                    view.context, view.request, view, method(view))
        else:
            def renderSubpath(view):
                return method(view)

        if self.name:
            subpaths[self.name] = renderSubpath
        else:
            subpaths[ob.__name__] = renderSubpath

        return ob
