import ptah
from ptah.testing import PtahTestCase
from pyramid.testing import DummyRequest
from pyramid.httpexceptions import HTTPFound
from pyramid.view import render_view_to_response


class TestSourceView(PtahTestCase):

    def test_source(self):
        from ptah.manage.source import SourceView
        from ptah.manage.manage import PtahManageRoute

        ptah.auth_service.set_userid(ptah.SUPERUSER_URI)

        request = DummyRequest()
        manage = PtahManageRoute(request)
        res = render_view_to_response(manage, request, 'source.html', False)
        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], '.')

    def test_source_view(self):
        from ptah.manage.source import SourceView
        from ptah.manage.manage import PtahManageRoute

        ptah.auth_service.set_userid(ptah.SUPERUSER_URI)

        request = DummyRequest(
            params = {'pkg': 'ptah.config'})
        manage = PtahManageRoute(request)
        res = render_view_to_response(manage, request, 'source.html', False)
        self.assertIn('Source: ptah/config.py', res.text)

    def test_source_view_unknown(self):
        from ptah.manage.source import SourceView
        from ptah.manage.manage import PtahManageRoute

        ptah.auth_service.set_userid(ptah.SUPERUSER_URI)

        request = DummyRequest(
            params = {'pkg': 'unknown'})
        manage = PtahManageRoute(request)
        res = render_view_to_response(manage, request, 'source.html', False)
        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], '.')
