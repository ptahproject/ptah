from zope import interface
from pyramid import security
from pyramid.security import Authenticated
from pyramid.security import Everyone
from pyramid.threadlocal import get_current_request
from pyramid.interfaces import IAuthorizationPolicy

import ptah
from role import LocalRoles
from interfaces import IAuthentication, ISearchableAuthProvider

checkers = []
providers = {}

def provideAuthChecker(checker):
    checkers.append(checker)

def registerProvider(name, provider):
    providers[name] = provider


class AuthInfo(object):

    def __init__(self, status=False, principal=None, message=u''):
        self.status = status
        self.principal = None
        self.message = message
        self.keywords = {}


class Authentication(object):
    interface.implements(IAuthentication)

    def authenticate(self, credentials):
        info = AuthInfo()
        
        for pname, provider in providers.items():
            principal = provider.authenticate(credentials)
            if principal is not None:
                info.principal = principal

                for checker in checkers:
                    if not checker(principal, info):
                        return info

                info.status = True
                return info

        return info

    def checkPrincipalAuth(self, principal):
        info = AuthInfo()
        info.principal = principal

        for checker in checkers:
            if not checker(principal, info):
                return info

        info.status = True
        return info

    def getPrincipalByLogin(self, login):
        for pname, provider in providers.items():
            principal = provider.getPrincipalInfoByLogin(login)
            if principal is not None:
                return principal

    def isAnonymous(self):
        id = security.authenticated_userid(get_current_request())
        if id:
            return False
        return True

    def getCurrentPrincipal(self):
        id = security.authenticated_userid(get_current_request())
        if id:
            return ptah.resolve(id)

    def search(self, term):
        for pname, provider in providers.items():
            if ISearchableAuthProvider.providedBy(provider):
                for principal in provider.search(term):
                    yield principal

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


authService = Authentication()
