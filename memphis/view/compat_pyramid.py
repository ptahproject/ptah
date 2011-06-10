""" pyramid view """
import sys
import martian
from zope import interface
from zope.interface import providedBy
from zope.component import getSiteManager

from webob.exc import HTTPForbidden
from pyramid.interfaces import \
    IRequest, IView, IViewClassifier, IAuthenticationPolicy

from memphis import config
from memphis.view.view import View
from memphis.view.directives import pyramidView, getInfo


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
        raise HTTPForbidden(msg)


registered = []
viewsExecuted = []

@config.cleanup
def cleanUp():
    registered[:] = []
    viewsExecuted[:] = []


class PyramidViewGrokker(martian.ClassGrokker):
    martian.component(View)
    martian.directive(pyramidView)

    _marker = object()

    def execute(self, klass, configContext=None, **kw):
        if klass in viewsExecuted:
            return False
        viewsExecuted.append(klass)

        value = pyramidView.bind(default=self._marker).get(klass)
        if value is self._marker:
            return False

        name, context, layer, template, \
            layout, permission, default, info = value
        if layer is None:
            layer = IRequest

        registerViewImpl(
            name, context, klass, template, layer, layout, permission,
            default, configContext, info)
        return True


def registerView(
    name='', context=None, klass=None, template=None,
    layer=IRequest, layout='', permission='', 
    default=False, configContext=None):

    config.action(
        registerViewImpl,
        name, context, klass, template, 
        layer, layout, permission, default, configContext, getInfo(),
        __frame = sys._getframe(1))


def registerViewImpl(
    name='', context=None, klass=None, template=None,
    layer=IRequest, layout='', permission='', 
    default=False, configContext=None, info=''):

    if permission == '__no_permission_required__':
        permission = None

    if klass is not None and klass in registered:
        raise ValueError("Class can be used for view only once.")

    cdict = {'__name__': name,
             'layoutname': layout}
    if template is not None:
        cdict['template'] = template

    if context is None:
        context = interface.Interface

    if klass is not None and issubclass(klass, View):
        registered.append(klass)
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

    if default:
        registerDefaultViewImpl(name, context, layer, configContext, info)


def registerDefaultView(name, context=interface.Interface,
                        layer=IRequest, configContext = None):

    config.action(
        registerDefaultViewImpl, name, context, layer, 
        configContext, getInfo(),
        __frame = sys._getframe(1))


def registerDefaultViewImpl(name, context=interface.Interface,
                            layer=IRequest, configContext = None, info=''):

    def view(context, request):
        return renderView(name, context, request)

    config.registerAdapter(
        view,
        (IViewClassifier, layer, context), IView, '', configContext, info)
