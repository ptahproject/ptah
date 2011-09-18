from zope import interface
from pyramid import security
from pyramid.security import Authenticated
from pyramid.security import Everyone
from pyramid.security import ACLDenied
from pyramid.threadlocal import get_current_request
from pyramid.interfaces import IAuthorizationPolicy
from pyramid.httpexceptions import HTTPForbidden

import ptah
from role import LocalRoles
from interfaces import IAuthentication, IAuthInfo

checkers = []
providers = {}
searchers = {}


def registerAuthChecker(checker):
    checkers.append(checker)


def registerProvider(name, provider):
    providers[name] = provider


def registerSearcher(name, searcher):
    searchers[name] = searcher


class AuthInfo(object):
    interface.implements(IAuthInfo)

    def __init__(self, status=False, principal=None, uuid=None, message=u''):
        self.status = status
        self.message = message
        self.keywords = {}
        self.principal = principal
        self.uuid = uuid
        

class Authentication(object):
    interface.implements(IAuthentication)

    def authenticate(self, credentials):
        info = AuthInfo()
        
        for pname, provider in providers.items():
            principal = provider.authenticate(credentials)
            if principal is not None:
                info.uuid = principal.uuid
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
        try:
            id = security.authenticated_userid(get_current_request())
        except:
            return None
        if id:
            return ptah.resolve(id)

authService = Authentication()


def checkPermission(context, permission, throw=True):
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

    res = authz.permits(context, principals, permission)

    if isinstance(res, ACLDenied):
        if throw:
            raise HTTPForbidden(res)

        return False
    return True


def searchPrincipals(term):
    for name, searcher in searchers.items():
        for principal in searcher(term):
            yield principal

