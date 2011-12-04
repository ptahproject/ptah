# -*- coding: utf-8 -*-
""" message tests """
import os
from zope import interface
from pyramid.compat import text_
from pyramid.interfaces import IRequest

from ptah import view
from ptah.testing import PtahTestCase
from ptah.view import get_message_service
from ptah.view.interfaces import IMessage, IStatusMessage


class TestStatusMessages(PtahTestCase):

    _init_ptah = False

    def test_messages_service(self, skip=False):
        if not skip:
            self.init_ptah()

        service = get_message_service(self.request)
        self.assertTrue(IStatusMessage.providedBy(service))
        self.assertEqual(service.messages(), ())

        # add simple msg
        service.add('Test')
        msgs = service.messages()
        self.assertTrue(len(msgs) == 1)
        self.assertTrue('Test' in msgs[0])

        # only one message
        service.add('Test')
        msgs = service.messages()
        self.assertTrue(len(msgs) == 1)

        # clear
        msgs = service.clear()
        self.assertTrue(len(msgs) == 1)
        self.assertTrue('Test' in msgs[0])
        self.assertEqual(service.messages(), ())

        self.assertEqual(service.clear(), ())

    def test_messages_addmessage(self):
        self.init_ptah()

        service = get_message_service(self.request)

        # add_message
        view.add_message(self.request, 'message')

        self.assertEqual(['\n'.join(service.clear()[0].split(os.linesep))],
                         [text_('<div class="alert-message info">\n  <a class="close" href="#">×</a>\n  <p>message</p>\n</div>\n','utf-8')])
        self.assertEqual(service.clear(), ())

    def test_messages_service_no_session(self):
        self.init_ptah()

        del self.request.session

        self.test_messages_service(True)

    def test_messages_warning_msg(self):
        self.init_ptah()

        service = get_message_service(self.request)

        # add simple msg
        service.add('warning', 'warning')
        self.assertEqual(
            ['\n'.join(service.clear()[0].split(os.linesep))],
            [text_('<div class="alert-message warning">\n  <a class="close" href="#">×</a>\n  <p>warning</p>\n</div>\n','utf-8')])

    def test_messages_error_msg(self):
        self.init_ptah()

        try:
            raise ValueError('Test')
        except:
            pass

        service = get_message_service(self.request)

        service.add('error', 'error')
        self.assertEqual(
            ['\n'.join(service.clear()[0].split(os.linesep))],
            [text_('<div class="alert-message error">\n  <a class="close" href="#">×</a>\n  <p>error</p>\n</div>\n','utf-8')])

        service.add(ValueError('Error'), 'error')
        self.assertEqual(
            ['\n'.join(service.clear()[0].split(os.linesep))],
            [text_('<div class="alert-message error">\n  <a class="close" href="#">×</a>\n  <p>ValueError: Error</p>\n</div>\n','utf-8')])

    def test_messages_custom_msg(self):
        class CustomMessage(object):
            interface.implements(IMessage)

            def __init__(self, request):
                self.request = request

            def render(self, message):
                return '<div class="customMsg">%s</div>'%message

        self.init_ptah()

        sm = self.registry
        sm.registerAdapter(CustomMessage, (IRequest,), IMessage, name='custom')

        service = get_message_service(self.request)

        service.add('message', 'custom')
        self.assertEqual(
            service.clear(),
            ['<div class="customMsg">message</div>'])

    def test_messages_render(self):
        self.init_ptah()

        view.add_message(self.request, 'message')
        msg = view.render_messages(self.request)
        self.assertEqual(
            '\n'.join(msg.split(os.linesep)),
            text_('<div class="alert-message info">\n  <a class="close" href="#">×</a>\n  <p>message</p>\n</div>\n','utf-8'))
        #self.assertEqual(type(msg), unicode)

        msg = view.render_messages(self.request)
        self.assertEqual(msg, '')

    def test_messages_View(self):
        self.init_ptah()

        v = view.View(None, self.request)

        v.message('message')

        service = get_message_service(self.request)

        self.assertEqual(
            ['\n'.join(service.messages()[0].split(os.linesep))],
            [text_('<div class="alert-message info">\n  <a class="close" href="#">×</a>\n  <p>message</p>\n</div>\n', 'utf-8')])
        self.assertEqual(
            '\n'.join(v.render_messages().split(os.linesep)),
            text_('<div class="alert-message info">\n  <a class="close" href="#">×</a>\n  <p>message</p>\n</div>\n', 'utf-8'))
        self.assertEqual(service.messages(), ())
