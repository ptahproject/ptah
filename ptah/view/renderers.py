""" renderers """
from pyramid.response import Response
from pyramid.httpexceptions import HTTPForbidden
from pyramid.interfaces import IAuthorizationPolicy
from pyramid.interfaces import IAuthenticationPolicy
from pyramid.threadlocal import get_current_registry


checkPermission = None

def set_checkpermission(func):
    global checkPermission
    checkPermission = func
    return func


@set_checkpermission
def default_checkpermission(permission, context, request=None, throw=False):
    AUTH = get_current_registry().queryUtility(IAuthenticationPolicy)
    if AUTH:
        AUTHZ = get_current_registry().queryUtility(IAuthorizationPolicy)
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

        if isinstance(result, Response):
            return result

        kwargs = {'view': view,
                  'context': context,
                  'request': request}
        if type(result) is dict:
            kwargs.update(result)

        request.response.content_type = self.content_type
        return self.template(**kwargs)
