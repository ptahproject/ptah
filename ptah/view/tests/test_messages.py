""" message tests """
import os
from zope import interface
from pyramid.interfaces import IRequest

from ptah import view
from ptah.view.interfaces import IMessage, IStatusMessage

from base import Base


class TestStatusMessages(Base):

    def _setup_ptah(self):
        pass

    def test_messages_service(self, skip=False):
        if not skip:
            self._init_ptah()

        service = IStatusMessage(self.request)
        self.assertTrue(IStatusMessage.providedBy(service))
        self.assertEqual(service.messages(), ())

        # add simple msg
        service.add('Test')
        msgs = service.messages()
        self.assertTrue(len(msgs) == 1)
        self.assertTrue(u'Test' in msgs[0])

        # only one message
        service.add('Test')
        msgs = service.messages()
        self.assertTrue(len(msgs) == 1)

        # clear
        msgs = service.clear()
        self.assertTrue(len(msgs) == 1)
        self.assertTrue(u'Test' in msgs[0])
        self.assertEqual(service.messages(), ())

        self.assertEqual(service.clear(), ())

    def test_messages_addmessage(self):
        self._init_ptah()

        service = IStatusMessage(self.request)

        # add_message
        view.add_message(self.request, 'message')

        self.assertEqual(['\n'.join(service.clear()[0].split(os.linesep))],
                         [u'<div class="alert-message info">\n  <a class="close" href="#">\xd7</a>\n  <p>message</p>\n</div>\n'])
        self.assertEqual(service.clear(), ())

    def test_messages_service_no_session(self):
        self._init_ptah()

        del self.request.session

        self.test_messages_service(True)

    def test_messages_warning_msg(self):
        self._init_ptah()

        service = IStatusMessage(self.request)

        # add simple msg
        service.add('warning', 'warning')
        self.assertEqual(
           ['\n'.join(service.clear()[0].split(os.linesep))],
           [u'<div class="alert-message warning">\n  <a class="close" href="#">\xd7</a>\n  <p>warning</p>\n</div>\n'])

    def test_messages_error_msg(self):
        self._init_ptah()

        try:
            raise ValueError('Test')
        except:
            pass

        service = IStatusMessage(self.request)

        service.add('error', 'error')
        self.assertEqual(
            ['\n'.join(service.clear()[0].split(os.linesep))],
            [u'<div class="alert-message error">\n  <a class="close" href="#">\xd7</a>\n  <p>error</p>\n</div>\n'])

        service.add(ValueError('Error'), 'error')
        self.assertEqual(
            ['\n'.join(service.clear()[0].split(os.linesep))],
            [u'<div class="alert-message error">\n  <a class="close" href="#">\xd7</a>\n  <p>ValueError: Error</p>\n</div>\n'])

    def test_messages_custom_msg(self):
        class CustomMessage(object):
            interface.implements(IMessage)

            def __init__(self, request):
                self.request = request

            def render(self, message):
                return '<div class="customMsg">%s</div>'%message

        self._init_ptah()

        sm = self.registry
        sm.registerAdapter(CustomMessage, (IRequest,), IMessage, name='custom')

        service = IStatusMessage(self.request)

        service.add('message', 'custom')
        self.assertEqual(
            service.clear(),
            [u'<div class="customMsg">message</div>'])

    def test_messages_render(self):
        self._init_ptah()

        view.add_message(self.request, 'message')
        msg = view.render_messages(self.request)
        self.assertEqual(
           '\n'.join(msg.split(os.linesep)),
           u'<div class="alert-message info">\n  <a class="close" href="#">\xd7</a>\n  <p>message</p>\n</div>\n')
        self.assertEqual(type(msg), unicode)

        msg = view.render_messages(self.request)
        self.assertEqual(msg, '')

    def test_messages_View(self):
        self._init_ptah()

        v = view.View(None, self.request)

        v.message('message')

        service = IStatusMessage(self.request)

        self.assertEqual(
            ['\n'.join(service.messages()[0].split(os.linesep))],
            [u'<div class="alert-message info">\n  <a class="close" href="#">\xd7</a>\n  <p>message</p>\n</div>\n'])
        self.assertEqual(
            '\n'.join(v.render_messages().split(os.linesep)),
            u'<div class="alert-message info">\n  <a class="close" href="#">\xd7</a>\n  <p>message</p>\n</div>\n')
        self.assertEqual(service.messages(), ())
