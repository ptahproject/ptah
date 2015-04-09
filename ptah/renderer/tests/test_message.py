# -*- coding: utf-8 -*-
""" Unit tests for L{ptah.renderer.message} """
from pyramid.compat import text_

from ptah.testing import BaseTestCase
from ptah.renderer.message import add_message
from ptah.renderer.message import render_messages


class TestStatusMessages(BaseTestCase):

    _includes = ['ptah.renderer']

    def test_messages_addmessage(self):
        add_message(self.request, 'message')

        res = render_messages(self.request).strip()

        self.assertEqual(
            res,
            text_('<div class="alert alert-info">\n  <a class="close" data-dismiss="alert">×</a>\n  message\n</div>','utf-8'))

    def test_messages_warning_msg(self):
        add_message(self.request, 'warning', 'warning')

        self.assertEqual(
            render_messages(self.request).strip(),
            text_('<div class="alert alert-warning">\n  <a class="close" data-dismiss="alert">×</a>\n  warning\n</div>','utf-8'))

    def test_messages_error_msg(self):
        add_message(self.request, 'error', 'error')

        self.assertEqual(
            render_messages(self.request).strip(),
            text_('<div class="alert alert-error alert-danger">\n  <a class="close" data-dismiss="alert">×</a>\n  error\n</div>','utf-8'))

        add_message(self.request, ValueError('Error'), 'error')
        self.assertEqual(
            render_messages(self.request).strip(),
            text_('<div class="alert alert-error alert-danger">\n  <a class="close" data-dismiss="alert">×</a>\n  ValueError: Error\n</div>','utf-8'))

    def test_multi_error(self):
        add_message(self.request, ['error1', ValueError('error2')], 'error')

        res = render_messages(self.request)
        self.assertIn('error1', res)
        self.assertIn('ValueError: error2', res)

    def test_messages_custom_msg(self):
        self.config.add_layer(
            'message', 'test', path='ptah.renderer:tests/message/')

        add_message(self.request, 'message', 'custom')
        self.assertEqual(
            render_messages(self.request).strip(),
            '<div class="customMsg">message</div>')

    def test_messages_custom_msg_different_type(self):
        self.config.add_layer(
            'test', path='ptah.renderer:tests/message/')

        add_message(self.request, 'message', 'test:custom')
        self.assertEqual(
            render_messages(self.request).strip(),
            '<div class="customMsg">message</div>')

    def test_messages_render_message_with_error(self):
        self.config.add_layer(
            'message', 'test', path='ptah.renderer:tests/messages/')

        def customMessage(context, request):
            raise ValueError()

        self.config.add_tmpl_filter('message:custom', customMessage)

        self.assertRaises(
            ValueError, add_message, self.request, 'message', 'custom')

    def test_messages_render(self):
        add_message(self.request, 'message')

        self.assertEqual(
            render_messages(self.request).strip(),
            text_('<div class="alert alert-info">\n  <a class="close" data-dismiss="alert">×</a>\n  message\n</div>','utf-8'))

        msg = render_messages(self.request)
        self.assertEqual(msg, '')

    def test_messages_unknown_type(self):
        from ptah.renderer import RendererNotFound

        self.assertRaises(
            RendererNotFound,
            add_message, self.request, 'message', 'unknown')

    def test_messages_request_attr(self):
        """
        Request has `add_message` and `render_messages` methods
        """
        req = self.make_request()
        req.add_message('message')

        res = req.render_messages().strip()

        self.assertEqual(
            res,
            text_('<div class="alert alert-info">\n  <a class="close" data-dismiss="alert">×</a>\n  message\n</div>','utf-8'))
