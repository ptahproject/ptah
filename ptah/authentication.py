import threading
from zope import interface
from memphis import config
from pyramid.interfaces import INewRequest
from pyramid.security import authenticated_userid
from pyramid.threadlocal import get_current_request

from ptah.uri import resolve
from ptah.interfaces import IAuthInfo, IAuthentication

checkers = []
providers = {}
searchers = {}


def registerAuthChecker(checker):
    checkers.append(checker)

    info = config.DirectiveInfo()
    info.attach(
        config.Action(None, discriminator = ('ptah:auth-checker', checker))
        )


def registerProvider(name, provider):
    providers[name] = provider

    info = config.DirectiveInfo()
    info.attach(
        config.Action(None, discriminator = ('ptah:auth-provider', name))
        )


def registerSearcher(name, searcher):
    searchers[name] = searcher

    info = config.DirectiveInfo()
    info.attach(
        config.Action(None, discriminator = ('ptah:auth-searcher', name))
        )


class AuthInfo(object):
    interface.implements(IAuthInfo)

    def __init__(self, status=False, principal=None, uri=None, message=u''):
        self.status = status
        self.message = message
        self.principal = principal
        self.uri = uri
        self.arguments = {}


_notSet = object()

class Authentication(threading.local):
    interface.implements(IAuthentication)

    uid = _notSet

    def authenticate(self, credentials):
        info = AuthInfo()

        for pname, provider in providers.items():
            principal = provider.authenticate(credentials)
            if principal is not None:
                info.uri = principal.uri
                info.principal = principal

                for checker in checkers:
                    if not checker(info):
                        return info

                info.status = True
                return info

        return info

    def authenticatePrincipal(self, principal):
        info = AuthInfo()
        info.uri = principal.uri
        info.principal = principal

        for checker in checkers:
            if not checker(info):
                return info

        info.status = True
        return info

    def setUserId(self, uid):
        self.uid = uid

    def getUserId(self):
        uid = getattr(self, 'uid', _notSet)
        if uid is _notSet:
            try:
                self.uid = authenticated_userid(get_current_request())
            except: # pragma: no cover
                self.uid = None
            return self.uid
        return uid

    def getCurrentPrincipal(self):
        uid = self.getUserId()
        if uid:
            return resolve(uid)

    def getPrincipalByLogin(self, login):
        for pname, provider in providers.items():
            principal = provider.getPrincipalByLogin(login)
            if principal is not None:
                return principal

authService = Authentication()


@config.handler(INewRequest)
def resetAuthCache(ev):
    authService.uid = _notSet
    authService.cache = {}


def searchPrincipals(term):
    for name, searcher in searchers.items():
        for principal in searcher(term):
            yield principal


@config.addCleanup
def cleanup():
    checkers[:] = []
    providers.clear()
    searchers.clear()
    authService.uid = _notSet
    authService.cache = {}
