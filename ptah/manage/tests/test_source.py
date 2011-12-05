from ptah.testing import PtahTestCase
from pyramid.testing import DummyRequest
from pyramid.httpexceptions import HTTPFound


class TestSourceView(PtahTestCase):

    def test_source(self):
        from ptah.manage.source import SourceView

        request = DummyRequest()
        res = SourceView.__renderer__(None, request)
        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], '.')

    def test_source_view(self):
        from ptah.manage.source import SourceView

        request = DummyRequest(
            params = {'pkg': 'ptah.config'})

        res = SourceView.__renderer__(None, request)
        self.assertIn('Source: ptah/config.py', res.text)

    def test_source_view_unknown(self):
        from ptah.manage.source import SourceView

        request = DummyRequest(
            params = {'pkg': 'unknown'})

        res = SourceView.__renderer__(None, request)
        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], '.')
