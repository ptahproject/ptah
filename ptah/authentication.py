import threading
from zope import interface
from memphis import config
from pyramid.interfaces import INewRequest
from pyramid.security import authenticated_userid
from pyramid.threadlocal import get_current_request

from ptah.uri import resolve
from ptah.util import tldata
from ptah.interfaces import IAuthInfo, IAuthentication

checkers = []
providers = {}
searchers = {}


class ManagerPrincipal(object):

    def __init__(self):
        self.uri = 'ptah+auth:superuser'
        self.login = ''
        self.name = 'Manager'

MANAGER = ManagerPrincipal()


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


_not_set = object()

USER_KEY = '__ptah_auth_userid__'


class Authentication(object):
    interface.implements(IAuthentication)

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
        tldata.set(USER_KEY, uid)

    def getUserId(self):
        uid = tldata.get(USER_KEY, _not_set)
        if uid is _not_set:
            try:
                self.setUserId(authenticated_userid(get_current_request()))
            except: # pragma: no cover
                self.setUserId(None)
            return tldata.get(USER_KEY)
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


def searchPrincipals(term):
    for name, searcher in searchers.items():
        for principal in searcher(term):
            yield principal


@config.addCleanup
def cleanup():
    checkers[:] = []
    providers.clear()
    searchers.clear()
