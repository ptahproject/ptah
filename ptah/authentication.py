import threading
from zope import interface
from memphis import config
from pyramid.interfaces import INewRequest
from pyramid.security import authenticated_userid
from pyramid.threadlocal import get_current_request

from ptah.uri import resolve, resolver
from ptah.util import tldata
from ptah.interfaces import IAuthInfo, IAuthentication

checkers = []
providers = {}
searchers = {}


class _Superuser(object):

    def __init__(self):
        self.uri = 'ptah+auth:superuser'
        self.login = ''
        self.name = 'Manager'

SUPERUSER = _Superuser()
SUPERUSER_URI = 'ptah+auth:superuser'

@resolver('ptah+auth', 'System super user')
def superuser_resolver(uri):
    if uri == SUPERUSER_URI:
        return SUPERUSER


def register_auth_checker(checker):
    checkers.append(checker)

    info = config.DirectiveInfo()
    info.attach(
        config.Action(
            lambda c: checkers.append(c), (checker,), 
            discriminator = ('ptah:auth-checker', checker))
        )
    return checker


def register_auth_provider(name, provider):
    providers[name] = provider

    info = config.DirectiveInfo()
    info.attach(
        config.Action(
            lambda n, p: providers.update({n:p}), (name, provider), 
            discriminator = ('ptah:auth-provider', name))
        )


def register_principal_searcher(name, searcher):
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

    def authenticate_principal(self, principal):
        info = AuthInfo()
        info.uri = principal.uri
        info.principal = principal

        for checker in checkers:
            if not checker(info):
                return info

        info.status = True
        return info

    def set_userid(self, uid):
        tldata.set(USER_KEY, uid)

    def get_userid(self):
        uid = tldata.get(USER_KEY, _not_set)
        if uid is _not_set:
            try:
                self.set_userid(authenticated_userid(get_current_request()))
            except: # pragma: no cover
                self.set_userid(None)
            return tldata.get(USER_KEY)
        return uid

    def get_current_principal(self):
        return resolve(self.get_userid())

    def get_principal_bylogin(self, login):
        for pname, provider in providers.items():
            principal = provider.get_principal_bylogin(login)
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
