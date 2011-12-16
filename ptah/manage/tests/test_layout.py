import sqlalchemy
from pyramid.testing import DummyRequest
from pyramid.httpexceptions import HTTPNotFound

import ptah
from ptah.testing import PtahTestCase


class _TestLayoutPreview(PtahTestCase):

    _init_ptah = False

    def test_layout_preview_notfound(self):
        from ptah.manage.layout import LayoutPreview

        request = DummyRequest()

        v = LayoutPreview(None,request)
        self.assertRaises(HTTPNotFound, v.update)

    def test_layout_preview_notfound2(self):
        from ptah.manage.layout import LayoutPreview

        class Context(object):
            """ """

        global View
        class View(object):
            ptah.view.pview('', Context)
            def render(self):
                return 'test' # pragma: no cover

        self.init_ptah()

        request = DummyRequest()

        v = LayoutPreview(Context(), request)
        self.assertRaises(HTTPNotFound, v.update)

    def test_layout_preview(self):
        from ptah.manage.layout import LayoutPreview

        class Context(object):
            """ """
            __name__ = 'test'

        def template(*args, **kw):
            return 'test'

        global View2
        class View2(ptah.view.View):
            ptah.view.pview('', Context, template=template)

            def update(self):
                """ """

        global Layout
        class Layout(ptah.view.Layout):
            ptah.view.layout('', Context, parent=None)

            def render(self, content):
                return '<div>%s</div>'%content

        self.init_ptah()

        request = DummyRequest()

        v = LayoutPreview(Context(), request)
        v.update()
        res = v.render()

        self.assertIn('<div style="border: 4px solid yellow">', res)
        self.assertIn('ptah.manage.tests.test_layout.Layout', res)
        self.assertIn('ptah.manage.tests.test_layout', res)
        self.assertIn('function template at', res)

    def test_layout_preview2(self):
        from ptah.manage.layout import LayoutPreview

        class Context(object):
            """ """
            __name__ = 'test'

        global View

        @ptah.view.pview('', Context, layout='')
        def View(context, request):
            return 'test' # pragma: no cover

        global Layout
        class Layout(ptah.view.Layout):
            ptah.view.layout('', Context, parent=None)

            template = 'layout template'

            def render(self, content):
                return '<div>%s</div>'%content

        self.init_ptah()

        request = DummyRequest()

        v = LayoutPreview(Context(), request)
        v.update()
        res = v.render()

        self.assertIn('<div style="border: 4px solid yellow">', res)
        self.assertIn('"view-factory": "View"', res)
        self.assertIn('layout template', res)
