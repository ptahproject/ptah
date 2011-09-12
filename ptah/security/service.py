from zope import interface
from pyramid import security
from pyramid.security import Authenticated
from pyramid.security import Everyone
from pyramid.threadlocal import get_current_request
from pyramid.interfaces import IAuthorizationPolicy

import ptah
from role import LocalRoles
from interfaces import IAuthentication, ISearchableAuthProvider

providers = {}


def registerProvider(name, provider):
    providers[name] = provider


class Principal(object):

    def __init__(self, id, name, login):
        self.id = id
        self.name = name
        self.login = login

    def __str__(self):
        return self.name


class Authentication(object):
    interface.implements(IAuthentication)

    def authenticate(self, credentials):
        for pname, provider in providers.items():
            info = provider.authenticate(credentials)
            if info is not None:
                id, name, login = info
                return Principal('user://%s:%s'%(pname, id), name, login)

    def getPrincipal(self, uri):
        if not uri or not uri.startswith('user://'):
            return

        uuid = uri.split('user://', 1)[1]
        pid, id = uuid.split(':', 1)

        provider = providers.get(pid)
        if provider is not None:
            info = provider.getPrincipalInfo(id)
            if info is not None:
                name, login = info
                return Principal(uri, name, login)

    def getPrincipalByLogin(self, login):
        for pname, provider in providers.items():
            info = provider.getPrincipalInfoByLogin(login)
            if info is not None:
                uuid, name, login = info
                return Principal('user://%s:%s'%(pname, uuid), name, login)

    def isAnonymous(self):
        id = security.authenticated_userid(get_current_request())
        if id:
            return False
        return True

    def getCurrentPrincipal(self):
        id = security.authenticated_userid(get_current_request())
        if id:
            return self.getPrincipal(id)

    def search(self, term):
        for pname, provider in providers.items():
            if ISearchableAuthProvider.providedBy(provider):
                for id, name, login in provider.search(term):
                    yield Principal('user://%s:%s'%(pname, id), name, login)

    def checkPermission(self, context, permission):
        if not permission or permission == '__no_permission_required__':
            return True

        principals = [Everyone]

        request = get_current_request()
        userid = security.authenticated_userid(request)
        if userid is not None:
            principals.append(Authenticated)

            roles = LocalRoles(userid, context=context)
            if roles:
                principals.extend(roles)

        authz = request.registry.queryUtility(IAuthorizationPolicy)
        return authz.permits(context, principals, permission)

    def _resolveUri(self, uri):
        return self.getPrincipal(uri)


authService = Authentication()

ptah.registerResolver(
    'user', None, authService._resolveUri, title='Principal resolver')
