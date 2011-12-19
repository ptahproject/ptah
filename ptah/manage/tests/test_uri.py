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
