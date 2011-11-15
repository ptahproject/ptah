""" role """
from ptah import config

from base import Base


class Principal(object):

    def __init__(self, uri, name, login):
        self.uri = uri
        self.name = name
        self.login = login


class TestAuthentication(Base):

    def tearDown(self):
        config.cleanup_system(self.__class__.__module__)
        super(TestAuthentication, self).tearDown()

    def test_auth_simple(self):
        import ptah

        info = ptah.authService.authenticate(
            {'login': 'user', 'password': '12345'})

        self.assertFalse(info.status)

        class Provider(object):
            def authenticate(self, creds):
                if creds['login'] == 'user':
                    return Principal('1', 'user', 'user')

        ptah.register_auth_provider('test-provider', Provider())
        self._init_ptah()

        info = ptah.authService.authenticate(
            {'login': 'user', 'password': '12345'})

        self.assertTrue(info.status)
        self.assertEqual(info.uri, '1')

    def test_auth_checker_default(self):
        import ptah
        self._init_ptah()

        principal = Principal('1', 'user', 'user')

        info = ptah.authService.authenticate_principal(principal)
        self.assertTrue(info.status)
        self.assertEqual(info.uri, '1')
        self.assertEqual(info.message, '')
        self.assertEqual(info.arguments, {})

    def test_auth_checker(self):
        import ptah

        principal = Principal('1', 'user', 'user')

        class Provider(object):
            def authenticate(self, creds):
                if creds['login'] == 'user':
                    return Principal('1', 'user', 'user')

        ptah.register_auth_provider('test-provider', Provider())

        @ptah.auth_checker
        def checker(info):
            info.message = 'Suspended'
            info.arguments['additional'] = 'test'
            return False

        self._init_ptah()

        info = ptah.authService.authenticate(
            {'login': 'user', 'password': '12345'})

        self.assertFalse(info.status)
        self.assertEqual(info.uri, '1')
        self.assertEqual(info.message, 'Suspended')
        self.assertEqual(info.arguments, {'additional': 'test'})

        principal = Principal('1', 'user', 'user')

        info = ptah.authService.authenticate_principal(principal)
        self.assertFalse(info.status)
        self.assertEqual(info.uri, '1')
        self.assertEqual(info.message, 'Suspended')
        self.assertEqual(info.arguments, {'additional': 'test'})

    def test_auth_get_set_userid(self):
        import ptah
        import ptah.util

        self.assertEqual(ptah.authService.get_userid(), None)

        ptah.authService.set_userid('user')
        self.assertEqual(ptah.authService.get_userid(), 'user')

        ptah.util.resetThreadLocalData(None)
        self.assertEqual(ptah.authService.get_userid(), None)

    def test_auth_principal(self):
        import ptah

        principal = Principal('1', 'user', 'user')
        def resolver(uri):
            if uri == 'test:1':
                return principal

        ptah.register_uri_resolver('test', resolver)
        self._init_ptah()

        self.assertEqual(ptah.authService.get_current_principal(), None)

        ptah.authService.set_userid('test:1')
        self.assertEqual(ptah.authService.get_current_principal(), principal)

    def test_auth_principal_login(self):
        import ptah

        principal = Principal('1', 'user', 'user')
        class Provider(object):
            def get_principal_bylogin(self, login):
                if login == 'user':
                    return principal

        ptah.register_auth_provider('test-provider', Provider())
        self._init_ptah()

        self.assertEqual(
            ptah.authService.get_principal_bylogin('user2'), None)

        self.assertEqual(
            ptah.authService.get_principal_bylogin('user'), principal)


class TestPrincipalSearcher(Base):

    def test_principal_searcher(self):
        import ptah

        principal = Principal('1', 'user', 'user')
        def search(term=''):
            if term == 'user':
                yield principal

        ptah.register_principal_searcher('test-provider', search)
        self._init_ptah()

        self.assertEqual(list(ptah.search_principals('user')), [principal])


class TestSuperUser(Base):

    def test_superuser_resolver(self):
        import ptah
        from ptah.authentication import SUPERUSER
        self._init_ptah()

        user = ptah.resolve(ptah.SUPERUSER_URI)
        self.assertIs(user, SUPERUSER)
        self.assertIsNone(ptah.resolve('ptah-auth:unknown'))
        self.assertEqual(repr(user), '<ptah Superuser>')
