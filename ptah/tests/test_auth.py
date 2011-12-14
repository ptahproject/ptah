from ptah import config
from ptah.testing import PtahTestCase
from pyramid import testing


class Principal(object):

    def __init__(self, uri, name, login):
        self.__uri__ = uri
        self.name = name
        self.login = login


class TestAuthentication(PtahTestCase):

    _init_ptah = False

    def test_auth_provider(self):
        import ptah

        info = ptah.auth_service.authenticate(
            {'login': 'user', 'password': '12345'})

        self.assertFalse(info.status)
        self.assertIsNone(info.principal)

        class Provider(object):
            def authenticate(self, creds):
                if creds['login'] == 'user':
                    return Principal('1', 'user', 'user')

        ptah.auth_provider.register('test-provider', Provider)
        self.init_ptah()

        info = ptah.auth_service.authenticate(
            {'login': 'user', 'password': '12345'})

        self.assertTrue(info.status)
        self.assertEqual(info.__uri__, '1')

    def test_auth_provider_declarative(self):
        import ptah

        @ptah.auth_provider('test-provider')
        class Provider(object):

            def authenticate(self, creds):
                if creds['login'] == 'user':
                    return Principal('1', 'user', 'user')

        self.init_ptah()

        info = ptah.auth_service.authenticate(
            {'login': 'user', 'password': '12345'})

        self.assertTrue(info.status)
        self.assertEqual(info.__uri__, '1')

    def test_auth_provider_pyramid(self):
        import ptah

        class Provider(object):
            def authenticate(self, creds):
                if creds['login'] == 'user':
                    return Principal('1', 'user', 'user')

        config = testing.setUp()
        config.include('ptah')

        self.assertTrue(getattr(config, 'ptah_auth_provider'))

        config.ptah_auth_provider('test-provider', Provider)
        config.commit()

        info = ptah.auth_service.authenticate(
            {'login': 'user', 'password': '12345'})

        self.assertTrue(info.status)
        self.assertEqual(info.__uri__, '1')

    def test_auth_checker_default(self):
        import ptah
        self.init_ptah()

        principal = Principal('1', 'user', 'user')

        info = ptah.auth_service.authenticate_principal(principal)
        self.assertTrue(info.status)
        self.assertEqual(info.__uri__, '1')
        self.assertEqual(info.message, '')
        self.assertEqual(info.arguments, {})

    def test_auth_checker(self):
        import ptah

        principal = Principal('1', 'user', 'user')

        class Provider(object):
            def authenticate(self, creds):
                if creds['login'] == 'user':
                    return Principal('1', 'user', 'user')

        ptah.auth_provider.register('test-provider', Provider)

        @ptah.auth_checker
        def checker(info):
            info.message = 'Suspended'
            info.arguments['additional'] = 'test'
            return False

        self.init_ptah()

        info = ptah.auth_service.authenticate(
            {'login': 'user', 'password': '12345'})

        self.assertFalse(info.status)
        self.assertEqual(info.__uri__, '1')
        self.assertEqual(info.message, 'Suspended')
        self.assertEqual(info.arguments, {'additional': 'test'})

        principal = Principal('1', 'user', 'user')

        info = ptah.auth_service.authenticate_principal(principal)
        self.assertFalse(info.status)
        self.assertEqual(info.__uri__, '1')
        self.assertEqual(info.message, 'Suspended')
        self.assertEqual(info.arguments, {'additional': 'test'})

    def test_auth_checker_pyramid(self):
        import ptah

        principal = Principal('1', 'user', 'user')

        class Provider(object):
            def authenticate(self, creds):
                if creds['login'] == 'user':
                    return Principal('1', 'user', 'user')

        config = testing.setUp()
        config.include('ptah')

        def checker(info):
            info.message = 'Suspended'
            info.arguments['additional'] = 'test'
            return False

        config.ptah_auth_checker(checker)
        config.ptah_auth_provider('test-provider', Provider)

        info = ptah.auth_service.authenticate(
            {'login': 'user', 'password': '12345'})

        self.assertFalse(info.status)
        self.assertEqual(info.__uri__, '1')
        self.assertEqual(info.message, 'Suspended')
        self.assertEqual(info.arguments, {'additional': 'test'})

        principal = Principal('1', 'user', 'user')

        info = ptah.auth_service.authenticate_principal(principal)
        self.assertFalse(info.status)
        self.assertEqual(info.__uri__, '1')
        self.assertEqual(info.message, 'Suspended')
        self.assertEqual(info.arguments, {'additional': 'test'})

    def test_auth_get_set_userid(self):
        import ptah
        import ptah.util

        self.assertEqual(ptah.auth_service.get_userid(), None)

        ptah.auth_service.set_userid('user')
        self.assertEqual(ptah.auth_service.get_userid(), 'user')

        ptah.util.resetThreadLocalData(None)
        self.assertEqual(ptah.auth_service.get_userid(), None)

    def test_auth_get_set_effective_userid(self):
        import ptah
        import ptah.util

        self.assertEqual(ptah.auth_service.get_effective_userid(), None)

        ptah.auth_service.set_effective_userid('user')
        self.assertEqual(ptah.auth_service.get_effective_userid(), 'user')

        ptah.util.resetThreadLocalData(None)
        self.assertEqual(ptah.auth_service.get_effective_userid(), None)

        ptah.auth_service.set_userid('user')
        self.assertEqual(ptah.auth_service.get_effective_userid(), 'user')

        ptah.auth_service.set_effective_userid('user2')
        self.assertEqual(ptah.auth_service.get_effective_userid(), 'user2')

        ptah.auth_service.set_userid('user3')
        self.assertEqual(ptah.auth_service.get_effective_userid(), 'user2')

    def test_auth_principal(self):
        import ptah

        principal = Principal('1', 'user', 'user')
        def resolver(uri):
            if uri == 'test:1':
                return principal

        ptah.resolver.register('test', resolver)
        self.init_ptah()

        self.assertEqual(ptah.auth_service.get_current_principal(), None)

        ptah.auth_service.set_userid('test:1')
        self.assertEqual(ptah.auth_service.get_current_principal(), principal)

    def test_auth_principal_login(self):
        import ptah

        principal = Principal('1', 'user', 'user')
        class Provider(object):
            def get_principal_bylogin(self, login):
                if login == 'user':
                    return principal

        ptah.auth_provider.register('test-provider', Provider)
        self.init_ptah()

        self.assertEqual(
            ptah.auth_service.get_principal_bylogin('user2'), None)

        self.assertEqual(
            ptah.auth_service.get_principal_bylogin('user'), principal)


class TestPrincipalSearcher(PtahTestCase):

    _init_ptah = False

    def test_principal_searcher(self):
        import ptah

        principal = Principal('1', 'user', 'user')
        def search(term=''):
            if term == 'user':
                yield principal

        ptah.principal_searcher.register('test-provider', search)
        self.init_ptah()

        self.assertEqual(list(ptah.search_principals('user')), [principal])

    def test_principal_searcher_pyramid(self):
        import ptah

        principal = Principal('1', 'user', 'user')
        def search(term=''):
            if term == 'user':
                yield principal

        config = testing.setUp()
        config.include('ptah')
        config.ptah_principal_searcher('test-provider', search)

        self.assertEqual(list(ptah.search_principals('user')), [principal])


class TestSuperUser(PtahTestCase):

    _init_ptah = False

    def test_superuser_resolver(self):
        import ptah
        from ptah.authentication import SUPERUSER
        self.init_ptah()

        user = ptah.resolve(ptah.SUPERUSER_URI)
        self.assertIs(user, SUPERUSER)
        self.assertIsNone(ptah.resolve('ptah-auth:unknown'))
        self.assertEqual(repr(user), '<ptah Superuser>')
