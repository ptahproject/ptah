# -*- coding: utf-8 -*-
""" view tests """
from pyramid.compat import text_

import ptah
from ptah.testing import PtahTestCase


class Context(object):
    pass


class TestView(PtahTestCase):

    _init_ptah = False

    def test_view_app_root(self):
        view = ptah.View(Context(), self.request)
        self.assertEqual(view.application_url, 'http://example.com')

        view = ptah.View(Context(), self.request)
        self.request.application_url = 'http://example.com/'
        self.assertEqual(view.application_url, 'http://example.com')


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
            text_('<div class="alert alert-info">\n  <a class="close" data-dismiss="alert">×</a>\n  message\n</div>\n','utf-8'))

    def test_messages_warning_msg(self):
        from ptah import view
        self.init_ptah()

        view.add_message(self.request, 'warning', 'warning')
        self.assertEqual(
            view.render_messages(self.request),
            text_('<div class="alert alert-warning">\n  <a class="close" data-dismiss="alert">×</a>\n  warning\n</div>\n','utf-8'))

    def test_messages_error_msg(self):
        from ptah import view
        self.init_ptah()

        view.add_message(self.request, 'error', 'error')
        self.assertEqual(
            view.render_messages(self.request),
            text_('<div class="alert alert-error">\n  <a class="close" data-dismiss="alert">×</a>\n  error\n</div>\n','utf-8'))

        view.add_message(self.request, ValueError('Error'), 'error')
        self.assertEqual(
            view.render_messages(self.request),
            text_('<div class="alert alert-error">\n  <a class="close" data-dismiss="alert">×</a>\n  ValueError: Error\n</div>\n','utf-8'))

    def test_messages_custom_msg(self):
        from ptah import view

        self.config.add_layer(
            'ptah-message', 'test', path='ptah:tests/messages/')
        self.init_ptah()

        view.add_message(self.request, 'message', 'custom')
        self.assertEqual(
            view.render_messages(self.request).strip(),
            '<div class="customMsg">message</div>')

    def test_messages_render_message(self):
        self.config.add_layer(
            'ptah-message', 'test', path='ptah:tests/messages/')
        self.init_ptah()

        self.assertEqual(
            ptah.render_message(self.request, 'message', 'custom').strip(),
            '<div class="customMsg">message</div>')
        self.assertEqual(
            ptah.render_message(
                self.request, 'message', 'ptah-message:custom').strip(),
            '<div class="customMsg">message</div>')

    def test_messages_render_message_with_error(self):
        self.config.add_layer('ptah-message', 'test',
                              path='ptah:tests/messages/')

        def customMessage(context, request):
            raise ValueError()

        self.config.add_tmpl_filter('ptah-message:custom', customMessage)

        self.init_ptah()

        self.assertRaises(
            ValueError,
            ptah.render_message, self.request, 'message', 'custom')

    def test_messages_render(self):
        from ptah import view
        self.init_ptah()

        view.add_message(self.request, 'message')
        self.assertEqual(
            view.render_messages(self.request),
            text_('<div class="alert alert-info">\n  <a class="close" data-dismiss="alert">×</a>\n  message\n</div>\n','utf-8'))

        msg = view.render_messages(self.request)
        self.assertEqual(msg, '')

    def test_messages_unknown_type(self):
        from ptah import view
        from pyramid_layer import RendererNotFound
        self.init_ptah()

        self.assertRaises(RendererNotFound,
                          view.add_message, self.request, 'message', 'unknown')

    def test_messages_request_attr(self):
        self.init_ptah()

        from pyramid.request import Request
        from pyramid.testing import DummySession
        from pyramid.interfaces import IRequestExtensions

        req = Request(environ=self._environ)
        req.registry = self.registry
        req.session = DummySession()

        extensions = self.registry.getUtility(IRequestExtensions)
        req._set_extensions(extensions)

        # add_message
        req.add_message('message')

        res = req.render_messages()

        self.assertEqual(
            res,
            text_('<div class="alert alert-info">\n  <a class="close" data-dismiss="alert">×</a>\n  message\n</div>\n','utf-8'))
