""" renderers """
import simplejson
from pyramid.response import Response
from pyramid.httpexceptions import HTTPForbidden
from pyramid.interfaces import IAuthorizationPolicy
from pyramid.interfaces import IAuthenticationPolicy

from ptah import config
from ptah.view.layout import query_layout


checkPermission = None

def set_checkpermission(func):
    global checkPermission
    checkPermission = func
    return func


@set_checkpermission
def default_checkpermission(permission, context, request=None, throw=False):
    AUTH = config.registry.queryUtility(IAuthenticationPolicy)
    if AUTH:
        AUTHZ = config.registry.queryUtility(IAuthorizationPolicy)
        if AUTHZ:
            principals = AUTH.effective_principals(request)
            return AUTHZ.permits(context, principals, permission)

    return True


class PermissionRenderer(object):

    def __init__(self, permission, factory):
        if callable(permission):
            def permChecker(context, request):
                if not permission(context, request):
                    msg = getattr(
                        request, 'authdebug_message',
                        'Unauthorized: %s failed permission check'%factory)
                    raise HTTPForbidden(msg)
        else:
            def permChecker(context, request):
                global checkPermission
                if not checkPermission(permission, context, request):
                    msg = getattr(
                        request, 'authdebug_message',
                        'Unauthorized: %s failed permission check'%factory)
                    raise HTTPForbidden(msg)
        self.checker = permChecker

    def __call__(self, context, request, content):
        self.checker(context, request)
        return content


class ViewRenderer(object):

    def __init__(self, factory, content_type='text/html'):
        self.factory = factory
        self.content_type = content_type

    def __call__(self, context, request, content):
        request.response.content_type = self.content_type
        return self.factory(context, request)[1]


class TemplateRenderer(ViewRenderer):

    def __init__(self, factory, template, content_type='text/html'):
        self.factory = factory
        self.template = template
        self.content_type = content_type

    def __call__(self, context, request, content):
        view, result = self.factory(context, request)

        kwargs = {'view': view,
                  'context': context,
                  'request': request}
        if type(result) is dict:
            kwargs.update(result)

        request.response.content_type = self.content_type
        return self.template(**kwargs)


class LayoutRenderer(object):

    def __init__(self, layout):
        self.layout = layout

    def __call__(self, context, request, content):
        layout = query_layout(request, context, self.layout)
        if layout is not None:
            content = layout(content)

        return content


class JSONRenderer(object):

    content_type = 'text/json'

    def __init__(self, content_type='text/json'):
        self.content_type = content_type

    def __call__(self, context, request, factory=None, dumps=simplejson.dumps):
        if not factory:
            factory = self.factory

        view, result = factory(context, request)

        response = request.response
        response.content_type = self.content_type
        response.body = dumps(result)
        return response


json = JSONRenderer()
