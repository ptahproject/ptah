from pyramid.security import authenticated_userid
from pyramid.threadlocal import get_current_request

import ptah
from ptah import config
from ptah.uri import resolve, resolver
from ptah.util import tldata


class _Superuser(object):
    """ Default ptah superuser. check_permission always pass with superuser """

    def __init__(self):
        self.__uri__ = 'ptah-auth:superuser'
        self.login = ''
        self.name = 'Manager'

    def __repr__(self):
        return '<ptah Superuser>'


SUPERUSER = _Superuser()
SUPERUSER_URI = 'ptah-auth:superuser'


@resolver('ptah-auth')
def superuser_resolver(uri):
    """System super user"""
    if uri == SUPERUSER_URI:
        return SUPERUSER


AUTH_CHECKER_ID = 'ptah:authchecker'
AUTH_PROVIDER_ID = 'ptah:authprovider'
AUTH_SEARCHER_ID = 'ptah:authsearcher'


def auth_checker(checker, __cfg=None, __depth=1):
    """Register authentication checker. Checker function accepts
    :py:class:`ptah.authentication.AuthInfo` object.

    :param checker: Checker function.

    Checker function interface :py:func:`ptah.interfaces.auth_checker`

    .. code-block:: python

      @ptah.auth_checker
      def my_checker(info):
          ...

    """
    info = config.DirectiveInfo(__depth)
    discr = (AUTH_CHECKER_ID, hash(checker))
    intr = config.Introspectable(
        AUTH_CHECKER_ID, discr, checker.__name__, AUTH_CHECKER_ID)
    intr['name'] = '{0}.{1}'.format(info.codeinfo.module, checker.__name__)
    intr['callable'] = checker
    intr['codeinfo'] = info.codeinfo

    info.attach(
        config.Action(
            lambda config, checker: config.get_cfg_storage(AUTH_CHECKER_ID)\
                .update({id(checker): checker}),
            (checker,), discriminator=discr, introspectables=(intr,)),
        __cfg)
    return checker


def pyramid_auth_checker(cfg, checker):
    """ Pyramid configurator directive for authentication
    checker registration.

    :param checker: Checker function

    Checker function interface :py:func:`ptah.interfaces.auth_checker`

    .. code-block:: python

      config = Configurator()
      config.include('ptah')

      def my_checker(info):
          ...

      config.ptah_auth_checker(my_checker)
    """
    auth_checker(checker, cfg, 3)


class auth_provider(object):
    """ Register authentication provider.
    Auth provider interface :py:class:`ptah.interfaces.AuthProvider`

    :param name: provider name

    .. code-block:: python

      @ptah.auth_provider('my-provider')
      class AuthProvider(object):
           ...

    """
    def __init__(self, name, __depth=1):
        self.info = config.DirectiveInfo(__depth)

        self.discr = (AUTH_PROVIDER_ID, name)
        self.intr = config.Introspectable(
            AUTH_PROVIDER_ID, self.discr, name, AUTH_PROVIDER_ID)
        self.intr['id'] = name
        self.intr['codeinfo'] = self.info.codeinfo

    def __call__(self, cls, __cfg=None):
        self.intr['provider'] = cls
        self.intr['name'] = '{0}.{1}'.format(
            self.info.codeinfo.module, cls.__name__)

        self.info.attach(
            config.Action(
                lambda config, n, p: config.get_cfg_storage(AUTH_PROVIDER_ID)\
                    .update({n: cls()}),
                (self.intr['name'], cls),
                discriminator=self.discr, introspectables=(self.intr,)),
            __cfg)
        return cls

    @classmethod
    def register(cls, name, provider):
        """ authentication provider registration::

        .. code-block:: python

          class AuthProvider(object):
             ...

          ptah.auth_provider.register('my-provider', AuthProvider)

        """
        cls(name, 2)(provider)

    @classmethod
    def pyramid(cls, cfg, name, provider):
        """ ``ptah_auth_provider`` directive implementation """
        cls(name, 3)(provider, cfg)


class AuthInfo(object):
    """ Authentication information """

    #: Principal uri or None if principal is not set
    __uri__ = None

    #: Principal object
    principal = None

    #: Status, True is principal has been authenticated, false otherwise
    status = False

    #: Extra message from auth checkers
    message = False

    def __init__(self, principal, status=False, message=''):
        self.__uri__ = getattr(principal, '__uri__', None)
        self.principal = principal
        self.status = status
        self.message = message
        self.arguments = {}


_not_set = object()

USER_KEY = '__ptah_userid__'
EFFECTIVE_USER_KEY = '__ptah_effective__userid__'


class Authentication(object):
    """ Ptah authentication utility """

    def authenticate(self, credentials):
        """Authenticate credentials.

        :param credentials: Dictionary with `login` and `password`
        :rtype: :py:class:`ptah.authentication.AuthInfo`
        """
        providers = config.get_cfg_storage(AUTH_PROVIDER_ID)
        for pname, provider in providers.items():
            principal = provider.authenticate(credentials)
            if principal is not None:
                info = AuthInfo(principal)

                for checker in \
                        config.get_cfg_storage(AUTH_CHECKER_ID).values():
                    if not checker(info):
                        return info

                info.status = True
                return info

        return AuthInfo(None)

    def authenticate_principal(self, principal):
        """Authenticate principal, check principal with
        auth checkers

        :param principal: Principal object
        :rtype: :py:class:`ptah.authentication.AuthInfo`
        """
        info = AuthInfo(principal)

        for checker in \
                config.get_cfg_storage(AUTH_CHECKER_ID).values():
            if not checker(info):
                return info

        info.status = True
        return info

    def set_userid(self, uri):
        """ Set current user id """
        tldata.set(USER_KEY, uri)

    def get_userid(self):
        """ Get current user id. By default it uses
        ``pyramid.security.authenticated_userid``"""
        uri = tldata.get(USER_KEY, _not_set)
        if uri is _not_set:
            self.set_userid(authenticated_userid(get_current_request()))
            return tldata.get(USER_KEY)
        return uri

    def set_effective_userid(self, uri):
        """ Set effective user uri """
        tldata.set(EFFECTIVE_USER_KEY, uri)

    def get_effective_userid(self):
        """ Return effective user uri, of current user uri. """
        uri = tldata.get(EFFECTIVE_USER_KEY, _not_set)
        if uri is _not_set:
            return self.get_userid()
        return uri

    def get_current_principal(self):
        """ Resolve and return current user uri """
        return resolve(self.get_userid())

    def get_principal_bylogin(self, login):
        """ Return principal by login """
        providers = config.get_cfg_storage(AUTH_PROVIDER_ID)

        for pname, provider in providers.items():
            principal = provider.get_principal_bylogin(login)
            if principal is not None:
                return principal

auth_service = Authentication()


def search_principals(term):
    """ Search principals by term, it uses principal_searcher functions """
    searchers = config.get_cfg_storage(AUTH_SEARCHER_ID)
    for name, searcher in searchers.items():
        for principal in searcher(term):
            yield principal


class principal_searcher(object):
    """ Register principal searcher function.

    Searcher function interface :py:func:`ptah.interfaces.principal_searcher`

    .. code-block:: python

      @ptah.principal_searcher('test')
      def searcher(term):
           ...

    searcher function receives text as term variable, and
    should return iterator to principal objects.
    """
    def __init__(self, name, __depth=1):
        self.info = config.DirectiveInfo(__depth)

        self.discr = (AUTH_SEARCHER_ID, name)
        self.intr = config.Introspectable(
            AUTH_SEARCHER_ID, self.discr, name, AUTH_SEARCHER_ID)
        self.intr['name'] = name

    def __call__(self, searcher, cfg=None):
        self.intr['callable'] = searcher

        self.info.attach(
            config.Action(
                lambda config, name, searcher:
                    config.get_cfg_storage(AUTH_SEARCHER_ID)\
                        .update({name: searcher}),
                (self.intr['name'], searcher),
                discriminator=self.discr, introspectables=(self.intr,)),
            cfg)

        return searcher

    @classmethod
    def register(cls, name, searcher):
        """ register principal searcher:

        .. code-block:: python

          def searcher(term):
              ...

          ptah.principal_searcher.register('test', searcher)

        """
        cls(name, 2)(searcher)

    @classmethod
    def pyramid(cls, cfg, name, searcher):
        """ pyramid configurator directive for
        principal searcher registration """
        cls(name, 3)(searcher, cfg)
