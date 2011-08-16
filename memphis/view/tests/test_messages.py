""" message tests """
import sys, unittest
from zope import component, interface
from pyramid.interfaces import IRequest

from memphis import config, view
from memphis.view.message import InformationMessage
from memphis.view.interfaces import IMessage, IStatusMessage

from base import Base

       
class TestStatusMessages(Base):

    def _setup_memphis(self):
        pass

    def _init_memphis(self, settings={}, handler=None, *args, **kw):
        config.begin()
        config.loadPackage('memphis.view')
        config.addPackage('memphis.view.tests.test_messages')
        config.commit()
        config.initializeSettings(settings, self.p_config)

    def test_messages_service(self, skip=False):
        if not skip:
            self._init_memphis()

        service = IStatusMessage(self.request)
        self.assertTrue(IStatusMessage.providedBy(service))
        self.assertEqual(service.messages(), ())

        # add simple msg
        service.add('Test')
        msgs = service.messages()
        self.assertTrue(len(msgs) == 1)
        self.assertTrue(u'<div class="statusMessage">Test</div>' in msgs)

        # only one message
        service.add('Test')
        msgs = service.messages()
        self.assertTrue(len(msgs) == 1)

        # clear
        msgs = service.clear()
        self.assertTrue(len(msgs) == 1)
        self.assertTrue(u'<div class="statusMessage">Test</div>' in msgs)
        self.assertEqual(service.messages(), ())

        self.assertEqual(service.clear(), ())

    def test_messages_addmessage(self):
        self._init_memphis()

        service = IStatusMessage(self.request)
        
        # addMessage
        view.addMessage(self.request, 'message')
        
        self.assertEqual(service.clear(), 
                         [u'<div class="statusMessage">message</div>'])
        self.assertEqual(service.clear(), ())

    def test_messages_service_no_session(self):
        self._init_memphis()

        del self.request.session

        service = IStatusMessage(self.request)
        self.test_messages_service(True)

    def test_messages_warning_msg(self):
        self._init_memphis()

        service = IStatusMessage(self.request)

        # add simple msg
        service.add('warning', 'warning')
        self.assertEqual(service.clear(), 
                         [u'<div class="statusWarningMessage">warning</div>'])

    def test_messages_error_msg(self):
        self._init_memphis()

        try:
            raise ValueError('Test')
        except:
            pass

        service = IStatusMessage(self.request)

        service.add('error', 'error')
        self.assertEqual(
            service.clear(), 
            [u'<div class="statusStopMessage">error</div>'])

        service.add(ValueError('Error'), 'error')
        self.assertEqual(
            service.clear(), 
            [u'<div class="statusStopMessage">ValueError: Error</div>'])

    def test_messages_custom_msg(self):
        class CustomMessage(object):
            interface.implements(IMessage)

            def __init__(self, request):
                self.request = request

            def render(self, message):
                return '<div class="customMsg">%s</div>'%message

        self._init_memphis()
            
        sm = component.getSiteManager()
        sm.registerAdapter(CustomMessage, (IRequest,), IMessage, name='custom')

        service = IStatusMessage(self.request)

        service.add('message', 'custom')
        self.assertEqual(
            service.clear(), 
            [u'<div class="customMsg">message</div>'])

    def test_messages_render(self):
        self._init_memphis()

        view.addMessage(self.request, 'message')
        msg = view.renderMessages(self.request)
        self.assertEqual(msg, '<div class="statusMessage">message</div>')
        self.assertEqual(type(msg), unicode)

        msg = view.renderMessages(self.request)
        self.assertEqual(msg, '')

    def test_messages_View(self):
        self._init_memphis()

        v = view.View(None, self.request)
        
        v.message('message')

        service = IStatusMessage(self.request)

        self.assertEqual(
            service.messages(),
            [u'<div class="statusMessage">message</div>'])
        self.assertEqual(
            v.renderMessages(),
            '<div class="statusMessage">message</div>')
        self.assertEqual(service.messages(), ())
