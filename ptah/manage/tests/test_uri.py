import ptah
from ptah.testing import PtahTestCase
from pyramid.testing import DummyRequest


class TestUriView(PtahTestCase):

    _cleanup_mod = False

    def test_uri_view(self):
        from ptah.manage.uri import UriResolver

        request = DummyRequest(
            GET = {'uri': 'ptah-auth:superuser'})

        view = UriResolver(None, request)
        view.update()

        self.assertEqual(view.data[0]['name'],
                         'ptah.authentication.superuser_resolver')

    def test_uri_handler(self):
        from ptah.manage.uri import UriResolver

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


class TestUriIntrospect(PtahTestCase):

    _cleanup_mod = False

    def _test_uri_introspect(self):
        from ptah.manage.uri import ID_RESOLVER
        from ptah.manage.intr_renderers import UriRenderer

        def resolver(uri): # pragma: no cover
            return 'Resolved'

        self.config.ptah_uri_resolver('uri-intro-test', resolver)

        data = ptah.config.scan(self.__class__.__module__, set())

        actions = []
        for action in data:
            if action.discriminator[0] == ID_RESOLVER:
                actions.append(action)

        ti = UriRenderer(self.request)
        res = ti(actions[0])

        self.assertIn('uri-intro-test', res)
        self.assertIn('ptah.manage.tests.test_uri', res)
