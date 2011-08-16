""" pyramid view """
import sys
import martian
from zope import interface
from zope.interface import providedBy
from zope.component import getSiteManager

from webob.exc import HTTPForbidden, HTTPException
from pyramid.interfaces import IView, IRequest
from pyramid.interfaces import IViewClassifier
from pyramid.interfaces import IAuthenticationPolicy

from memphis import config
from memphis.view.view import View, SimpleView, subpathWrapper
from memphis.view.directives import pyramidView


def renderView(name, context, request):
    adapters = getSiteManager().adapters

    view_callable = adapters.lookup(
        (IViewClassifier, providedBy(request), providedBy(context)),
        IView, name=name, default=None)

    return view_callable(context, request)


class PyramidView(object):

    def __init__(self, factory):
        self.factory = factory

    def __call__(self, context, request):
        return self.factory(context, request)()


class SecuredPyramidView(object):

    def __init__(self, factory, auth, permission):
        self.factory = factory
        self.auth = auth
        self.permission = permission

    def __call__(self, context, request):
        principals = self.auth.effective_principals(request)
        if self.auth.permits(context, principals, self.permission):
            try:
                return self.factory(context, request)()
            except HTTPException, exc:
                return exc
        msg = getattr(request, 'authdebug_message',
                      'Unauthorized: %s failed permission check' % self.factory)
        raise HTTPForbidden(msg)


def registerView(
    name, klass=View, context=None, template=None,
    layer=IRequest, layout='', permission='__no_permission_required__', 
    default=False, decorator=None, configContext=config.UNSET):

    if not klass or not issubclass(klass, SimpleView):
        raise ValueError("klass has to inherit from SimpleView class")

    info = config.getInfo(2)

    config.action(
        registerViewImpl,
        name, klass, context, template, 
        layer, layout, permission, default, decorator, configContext, info,
        __info = info,
        __frame = sys._getframe(1),
        __discriminator = ('memphis.view:view', name, context, layer))


_viewclasses = (View, SimpleView)

def registerViewImpl(
    name, klass, context, template, layer, layout, permission, 
    default, decorator, configContext=config.UNSET, info=''):

    if klass is not None and klass in _registered:
        raise ValueError("Class can be used for view only once.")

    if permission == '__no_permission_required__':
        permission = None

    cdict = {'__name__': name}
    if layout or layout is None:
        cdict['layout'] = layout
    if template is not None:
        cdict['template'] = template
    if context is None:
        context = interface.Interface

    if issubclass(klass, _viewclasses) and klass not in _viewclasses:
        _registered.append(klass)
        view_class = klass
        for attr, value in cdict.items():
            setattr(view_class, attr, value)
    else:
        view_class = type('View %s'%klass, (klass,), cdict)

    # add 'subpath' support
    subpathWrapper(view_class)

    # decorate view class
    if decorator:
        view_class = decorator(view_class)

    auth = getSiteManager().queryUtility(IAuthenticationPolicy)
    if auth and permission:
        view = SecuredPyramidView(view_class, auth, permission)
    else:
        view = PyramidView(view_class)

    config.registerAdapter(
        view,
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


_registered = []

@config.cleanup
def cleanUp():
    _registered[:] = []
