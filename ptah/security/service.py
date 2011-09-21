import threading
from memphis import config, view
from zope import interface
from zope.component import getUtility
from pyramid.security import Authenticated
from pyramid.security import ACLDenied
from pyramid.security import Everyone
from pyramid.security import authenticated_userid
from pyramid.threadlocal import get_current_request
from pyramid.interfaces import INewRequest, IAuthorizationPolicy
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
        

_notSet = object()

class Authentication(threading.local):
    interface.implements(IAuthentication)

    uid = _notSet

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
        return not self.getUserId()

    def setUserId(self, uid):
        self.uid = uid

    def getUserId(self):
        uid = getattr(self, 'uid', _notSet)
        if uid is _notSet:
            try:
                self.uid = authenticated_userid(get_current_request())
            except:
                self.uid = None
            return self.uid
        return uid

    def getCurrentPrincipal(self):
        uid = self.getUserId()
        if uid:
            return ptah.resolve(uid)

authService = Authentication()


@config.handler(INewRequest)
def resetUserId(ev):
    authService.uid = _notSet
    authService.cache = {}


def checkPermission(context, permission, request=None, throw=True):
    if not permission or permission == '__no_permission_required__':
        return True

    global AUTHZ
    try:
        AUTHZ
    except:
        AUTHZ = getUtility(IAuthorizationPolicy)

    principals = [Everyone]

    userid = authService.getUserId()
    if userid is not None:
        principals.append(Authenticated)

        roles = LocalRoles(userid, context=context)
        if roles:
            principals.extend(roles)

    res = AUTHZ.permits(context, principals, permission)

    if isinstance(res, ACLDenied):
        if throw:
            raise HTTPForbidden(res)

        return False
    return True

view.setCheckPermission(checkPermission)


def searchPrincipals(term):
    for name, searcher in searchers.items():
        for principal in searcher(term):
            yield principal
