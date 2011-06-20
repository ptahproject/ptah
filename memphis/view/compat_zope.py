""" zope related classes """
import sys, martian
from webob import Response
from AccessControl import Unauthorized, getSecurityManager
from Products.statusmessages.interfaces import \
    IStatusMessage as ZopeIStatusMessage

from zope import interface
from zope.publisher.interfaces import IDefaultViewName
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from memphis import config
from memphis.view.view import View
from memphis.view.layout import Layout
from memphis.view.directives import zopeView, getInfo
from memphis.view.interfaces import IStatusMessage


class ZopeLayout(object):

    def render(self):
        if self.template is None:
            raise RuntimeError("Can't render layout: %s"%self.__name__)

        template = self.template.im_func

        namespace = template.pt_getContext(self.view, request=self.request)

        kwargs = self._params or {}
        kwargs.update({'view': self.view,
                       'context': self.view.context,
                       'layout': self,
                       'layoutcontext': self.context,
                       'mainview': self.mainview,
                       'maincontext': self.maincontext,
                       'request': self.request,
                       'template': template,
                       'nothing': None})
        namespace.update(kwargs)

        return template.pt_render(namespace, showtal= 0, sourceAnnotations= 0)


class ZopeView(object):

    def __init__(self, context, request, factory):
        self.factory = factory
        self.context = context
        self.request = request

    def __call__(self):
        inst = self.factory(self.context, self.request)

        res = inst()
        if isinstance(res, Response):
            response = self.request.response
            response.setStatus(res.status_int)
            for key, val in res.headers.items():
                response.setHeader(key, val)

            return res.body

        return res


class SecuredZopeView(ZopeView):

    def __init__(self, context, request, factory, permission):
        self.factory = factory
        self.permission = permission
        self.context = context
        self.request = request

    def __call__(self):
        if getSecurityManager().checkPermission(self.permission, self.context):
            return super(SecuredZopeView, self).__call__()

        raise Unauthorized()


registered = []
viewsExecuted = []

@config.cleanup
def cleanUp():
    registered[:] = []
    viewsExecuted[:] = []


class ZopeViewGrokker(martian.ClassGrokker):
    martian.component(View)
    martian.directive(zopeView)

    _marker = object()

    def execute(self, klass, configContext=config.UNSET, **kw):
        if klass in viewsExecuted:
            return False
        viewsExecuted.append(klass)

        value = zopeView.bind(default=self._marker).get(klass)
        if value is self._marker:
            return False

        name, context, layer, template, \
            layout, permission, default, decorator, info = value
        if layer is None:
            layer = IDefaultBrowserLayer

        config.addAction(
            configContext,
            discriminator = ('memphis.view:zopeView', name, context, layer),
            callable = registerViewImpl,
            args = (name, context, klass, template, layer, layout, permission,
                    default, decorator),
            order = (config.moduleNum(klass.__module__), 300),
            info = info)
        return True


def registerZopeView(
    name='', context=None, klass=None, template=None,
    layer=IDefaultBrowserLayer, layout='', permission='', default=False, 
    decorator=None, configContext=config.UNSET):
    
    frame = sys._getframe(1)

    config.action(
        registerViewImpl,
        name, context, klass, template, 
        layer, layout, permission, default, decorator, configContext, 
        getInfo(), __frame = frame)
        #discriminator = ('memphis.view:zopeView', name, context, layer),
        #actionOrder = (config.moduleNum(frame.f_locals['__name__']), 300))


def registerViewImpl(
    name='', context=None, klass=None, template=None,
    layer=IDefaultBrowserLayer, layout='', permission='', default=False,
    decorator=None, configContext=config.UNSET, info=''):

    if permission in ('zope2.Public', 'zope.Public'):
        permission = None

    if klass is not None and klass in registered:
        raise ValueError("Class can be used for view only once.")

    cdict = {'__name__': name,
             'layoutname': layout,
             'template': template}

    if context is None:
        context = interface.Interface

    if klass is not None and issubclass(klass, View):
        registered.append(klass)
        view_class = klass
        del cdict['__name__']

        for attr, value in cdict.items():
            setattr(view_class, attr, value)
    else:
        # Build a new class
        if klass is None:
            bases = (View, )
        else:
            bases = (klass, View)

        view_class = type('View %s'%klass, bases, cdict)

    if decorator is not None:
        view_class = decorator(view_class)

    if permission:
        def zview(context, request):
            return SecuredZopeView(context, request, view_class, permission)
    else:
        def zview(context, request):
            return ZopeView(context, request, view_class)

    config.registerAdapter(
        zview,
        (context, layer), interface.Interface, name, configContext, info)

    if default:
        registerDefaultViewImpl(name, context, layer, configContext, info)


def registerZopeDefaultView(
    name, context=interface.Interface, 
    layer=IDefaultBrowserLayer, configContext=config.UNSET):

    frame = sys._getframe(1)
    
    config.action(
        registerDefaultViewImpl, name, context, layer, 
        configContext, getInfo(), __frame = frame,
        )
        #discriminator = ('memphis.view:defaultZopeView', name, context),
        #actionOrder = (config.moduleNum(frame.f_locals['__name__']), 300))


def registerDefaultViewImpl(
    name, context=interface.Interface,
    layer=IDefaultBrowserLayer, configContext=config.UNSET, info=''):

    config.registerAdapter(
        name,
        (context, layer), IDefaultViewName, '', configContext, info)


@config.adapter(IDefaultBrowserLayer)
@interface.implementer(IStatusMessage)
def getMessageService(request):
    return ZopeIStatusMessage(request)
