import sqlalchemy
from pyramid.compat import text_
from pyramid.testing import DummyRequest
from pyramid.httpexceptions import HTTPNotFound

import ptah


class TestLayoutPreview(ptah.PtahTestCase):

    _init_ptah = False

    def test_layout_preview_notfound(self):
        from ptah.manage.layout import layoutPreview

        request = DummyRequest()

        res = layoutPreview(None,request)
        self.assertIsInstance(res, HTTPNotFound)

    def test_layout_preview(self):
        from ptah.manage.layout import layoutPreview

        class Context(object):
            """ """
            __name__ = 'test'

        def View(context, request):
            request.response.text = text_('test body')
            return request.response

        self.init_ptah()

        self.config.add_view(
            name='', context=Context, wrapper=ptah.wrap_layout(), view=View,)
        self.config.ptah_layout(
            '', parent='page', context=Context,
            renderer='ptah.manage:tests/test_layout.pt')

        request = DummyRequest()

        res = layoutPreview(Context(), request).text

        self.assertIn('"python-module": "ptah.manage.tests.test_layout"', res)
        self.assertIn('"renderer": "ptah.manage:tests/test_layout.pt"', res)
