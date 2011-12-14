# -*- coding: utf-8 -*-
""" snippet tests """
from pyramid.compat import text_
from zope.interface import providedBy

import ptah
from ptah import config, view
from ptah.testing import PtahTestCase


class Context(object):
    pass


class TestView(PtahTestCase):

    _init_ptah = False

    def test_snippet_app_root(self):
        view = ptah.View(Context(), self.request)
        self.assertEqual(view.application_url, 'http://example.com')

        view = ptah.View(Context(), self.request)
        self.request.application_url = 'http://example.com/'
        self.assertEqual(view.application_url, 'http://example.com')

    def test_snippet_View(self):
        def TestSnippet(request):
            return 'test snippet'

        ptah.snippet.register('test', Context, TestSnippet)
        self.init_ptah()

        view = ptah.View(Context(), self.request)
        self.assertEqual(view.snippet('test'), 'test snippet')

    def test_snippet_View_with_error(self):
        def TestSnippet(request):
            raise 'Error'

        ptah.snippet.register('test', Context, TestSnippet)
        self.init_ptah()

        view = ptah.View(Context(), self.request)
        self.assertEqual(view.snippet('test'), '')

    def test_messages_View(self):
        from ptah import view
        self.init_ptah()

        v = view.View(None, self.request)
        v.message('message')

        self.assertEqual(
            v.render_messages(),
            text_('<div class="alert-message info">\n  <a class="close" href="#">×</a>\n  <p>message</p>\n</div>\n', 'utf-8'))


class TestSnippet(PtahTestCase):

    _init_ptah = False

    def test_snippet_register(self):
        def TestSnippet(request):
            return 'test snippet'

        view.snippet.register('test', Context, TestSnippet)
        self.init_ptah()

        res = self.registry.adapters.lookup(
            (providedBy(Context()), providedBy(self.request)),
            view.ISnippet, 'test')

        self.assertEqual(res(Context(), self.request), 'test snippet')

    def test_snippet_register_render_snippet(self):
        def TestSnippet(request):
            return 'test snippet'

        view.snippet.register('test', Context, TestSnippet)
        self.init_ptah()

        res = view.render_snippet('test', Context(), self.request)
        self.assertEqual(res.strip(), 'test snippet')

        self.assertRaises(
            Exception,
            view.render_snippet, 'unknown', Context(), self.request)

    def test_snippet_register_declarative(self):
        @view.snippet('pt')
        class TestSnippet(view.View):

            def __call__(self):
                return 'test'

        self.init_ptah()

        res = self.registry.getMultiAdapter(
            (Context(), self.request), view.ISnippet, 'pt')

        self.assertEqual(res, 'test')

    def test_snippet_register_pyramid(self):
        from pyramid.config import Configurator

        class TestSnippet(view.View):
            def __call__(self):
                return 'test'

        config = Configurator(autocommit=True)
        config.include('ptah')
        config.ptah_snippet('pt', view=TestSnippet)

        res = config.registry.getMultiAdapter(
            (Context(), self.request), view.ISnippet, 'pt')
        self.assertEqual(res, 'test')

    def test_snippet_register_with_renderer(self):

        @view.snippet('test', renderer='ptah:tests/test.pt')
        class TestSnippet(view.View):
            def __call__(self):
                return None

        self.init_ptah()

        res = self.registry.getMultiAdapter(
            (Context(), self.request), view.ISnippet, 'test')

        self.assertEqual(res.strip(), '<div>My snippet</div>')

    def test_snippet_register_without_class(self):
        view.snippet.register(
            'test', Context, renderer='ptah:tests/test.pt')
        self.init_ptah()

        res = self.registry.queryMultiAdapter(
            (Context(), self.request), view.ISnippet, 'test')

        self.assertEqual(res.strip(), '<div>My snippet</div>')


class TestStatusMessages(PtahTestCase):

    _init_ptah = False

    def test_messages_addmessage(self):
        from ptah import view
        self.init_ptah()

        # add_message
        view.add_message(self.request, 'message')

        res = view.render_messages(self.request)

        self.assertEqual(
            res,
            text_('<div class="alert-message info">\n  <a class="close" href="#">×</a>\n  <p>message</p>\n</div>\n','utf-8'))

    def test_messages_warning_msg(self):
        from ptah import view
        self.init_ptah()

        view.add_message(self.request, 'warning', 'warning')
        self.assertEqual(
            view.render_messages(self.request),
            text_('<div class="alert-message warning">\n  <a class="close" href="#">×</a>\n  <p>warning</p>\n</div>\n','utf-8'))

    def test_messages_error_msg(self):
        from ptah import view
        self.init_ptah()

        view.add_message(self.request, 'error', 'error')
        self.assertEqual(
            view.render_messages(self.request),
            text_('<div class="alert-message error">\n  <a class="close" href="#">×</a>\n  <p>error</p>\n</div>\n','utf-8'))

        view.add_message(self.request, ValueError('Error'), 'error')
        self.assertEqual(
            view.render_messages(self.request),
            text_('<div class="alert-message error">\n  <a class="close" href="#">×</a>\n  <p>ValueError: Error</p>\n</div>\n','utf-8'))

    def test_messages_custom_msg(self):
        from ptah import view

        @view.snippet('custom', view.Message)
        def customMessage(context, request):
            return '<div class="customMsg">{0}</div>'.format(context.message)

        self.init_ptah()

        view.add_message(self.request, 'message', 'custom')
        self.assertEqual(
            view.render_messages(self.request),
            '<div class="customMsg">message</div>')

    def test_messages_render(self):
        from ptah import view
        self.init_ptah()

        view.add_message(self.request, 'message')
        self.assertEqual(
            view.render_messages(self.request),
            text_('<div class="alert-message info">\n  <a class="close" href="#">×</a>\n  <p>message</p>\n</div>\n','utf-8'))

        msg = view.render_messages(self.request)
        self.assertEqual(msg, '')

    def test_messages_unknown_type(self):
        from ptah import view
        self.init_ptah()

        view.add_message(self.request, 'message', 'unknown')
        self.assertEqual(
            view.render_messages(self.request),
            text_('message','utf-8'))
