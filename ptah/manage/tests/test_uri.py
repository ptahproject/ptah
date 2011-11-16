import ptah
from pyramid.testing import DummyRequest

from base import Base


class TestUriView(Base):

    def setUp(self):
        self._setup_pyramid()

    def test_uri_view(self):
        from ptah.manage.uri import UriResolver
        self._init_ptah()

        request = DummyRequest(
            GET = {'uri': 'ptah-auth:superuser'})

        view = UriResolver(None, request)
        view.update()

        self.assertEqual(view.data[0]['name'],
                         'ptah.authentication.superuser_resolver')

    def test_uri_handler(self):
        from ptah.manage.uri import UriResolver
        self._init_ptah()

        request = DummyRequest(
            POST = {'form.buttons.show': 'Show'})

        view = UriResolver(None, request)
        view.update()

        request = DummyRequest(
            POST = {'form.buttons.show': 'Show', 'uri': 'ptah-auth:superuser'})

        view = UriResolver(None, request)
        view.update()

        self.assertEqual(view.data[0]['name'],
                         'ptah.authentication.superuser_resolver')


@ptah.resolver('uri-intro-test')
def resolver(uri): # pragma: no cover
    return 'Resolved'


class TestUriIntrospect(Base):

    def test_uri_introspect(self):
        from ptah.config import directives
        from ptah.manage.uri import RESOLVER_ID, UriIntrospection

        data = directives.scan(self.__class__.__module__, set())

        actions = []
        for action in data:
            if action.discriminator[0] == RESOLVER_ID:
                actions.append(action)

        ti = UriIntrospection(self.request)
        res = ti.renderActions(*actions)

        self.assertIn('uri-intro-test', res)
        self.assertIn('ptah.manage.tests.test_uri', res)
