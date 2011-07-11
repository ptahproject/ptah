""" pyramid view """
import sys
import martian
from zope import interface
from zope.interface import providedBy
from zope.component import getSiteManager, queryUtility

from webob.exc import HTTPForbidden, HTTPException
from pyramid.interfaces import IView, IViewClassifier
from pyramid.interfaces import IRequest, INewResponse
from pyramid.interfaces import IAuthenticationPolicy

from memphis import config
from memphis.view.view import View
from memphis.view.directives import pyramidView, getInfo

from memphis.view.message import MessageService
from memphis.view.interfaces import IStatusMessage


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
        try:
            return self.factory(context, request)()
        except HTTPException, exc:
            return exc


class SecuredPyramidView(PyramidView):

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


class PyramidViewGrokker(martian.ClassGrokker):
    martian.component(View)
    martian.directive(pyramidView)

    _marker = object()

    def execute(self, klass, configContext=config.UNSET, **kw):
        if klass in viewsExecuted:
            return False
        viewsExecuted.append(klass)

        value = pyramidView.bind(default=self._marker).get(klass)
        if value is self._marker:
            return False

        name, context, layer, template, \
            layout, permission, default, decorator, info = value
        if layer is None:
            layer = IRequest

        registerViewImpl(
            name, context, klass, template, layer, layout, permission,
            default, decorator, configContext, info)
        return True


def registerView(
    name='', context=None, klass=None, template=None,
    layer=IRequest, layout=None, permission='', 
    default=False, decorator=None, configContext=config.UNSET):

    config.action(
        registerViewImpl,
        name, context, klass, template, 
        layer, layout, permission, default, decorator, configContext, getInfo(),
        __frame = sys._getframe(1))


def registerViewImpl(
    name='', context=None, klass=None, template=None,
    layer=IRequest, layout='', permission='', 
    default=False, decorator=None, configContext=config.UNSET, info=''):

    if permission == '__no_permission_required__':
        permission = None

    if klass is not None and klass in registered:
        raise ValueError("Class can be used for view only once.")

    cdict = {'__name__': name}
    if layout is not None:
        cdict['layout'] = layout
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

    if decorator:
        view_class = decorator(view_class)

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
                        layer=IRequest, configContext = config.UNSET):

    config.action(
        registerDefaultViewImpl, name, context, layer, 
        configContext, getInfo(),
        __frame = sys._getframe(1))


def registerDefaultViewImpl(
    name, context=interface.Interface,
    layer=IRequest, configContext = config.UNSET, info=''):

    def view(context, request):
        return renderView(name, context, request)

    config.registerAdapter(
        view,
        (IViewClassifier, layer, context), IView, '', configContext, info)


@config.adapter(IRequest)
@interface.implementer(IStatusMessage)
def getMessageService(request):
    service = queryUtility(IStatusMessage)
    if service is None:
        service = MessageService(request)
    return service


@config.handler(INewResponse)
def responseHandler(event):
    request = event.request
    response = event.response

    if (response.status == '200 OK') and (response.content_type == 'text/html'):
        service = IStatusMessage(request, None)
        if service is not None:
            messages = service.clear()
            if messages:
                msg = u'\n'.join(messages)
                msg = msg.encode('utf-8', 'ignore')

                body = response.body
                body = body.replace('<!--memphis-message-->', msg, 1)
                response.body = body



registered = []
viewsExecuted = []

@config.cleanup
def cleanUp():
    registered[:] = []
    viewsExecuted[:] = []
