from zope.interface import implementedBy
from pyramid.config import Configurator
from pyramid.exceptions import ConfigurationError, ConfigurationConflictError
from pyramid.httpexceptions import HTTPNotFound

import ptah
from ptah.testing import unittest

try:
    import pyramid_sockjs
    has_sockjs = True
except ImportError:
    has_sockjs = False


@unittest.skipUnless(has_sockjs, 'No pyramid_sockjs')
class TestInitDirective(ptah.PtahTestCase):

    _init_ptah = False

    def test_init_sockjs_directive(self):
        self.assertFalse(hasattr(self.config, 'ptah_init_sockjs'))
        self.config.include('ptah')
        self.config.include('pyramid_sockjs')

        self.assertTrue(hasattr(self.config, 'ptah_init_sockjs'))

        self.config.ptah_init_sockjs()
        self.assertIsNotNone(
            pyramid_sockjs.get_session_manager('ptah', self.registry))


@unittest.skipUnless(has_sockjs, 'No pyramid_sockjs')
class TestProtocolDirective(ptah.PtahTestCase):

    _auto_commit = False

    def test_protocol(self):
        global TestProtocol

        @ptah.sockjs.protocol('test')
        class TestProtocol(ptah.sockjs.Protocol):
            pass

        self.config.scan(self.__class__.__module__)
        self.config.commit()

        from ptah.sockjs.session import IProtocol, Session
        item = self.config.registry.adapters.lookup(
            (implementedBy(Session),), IProtocol, name='test')

        self.assertIs(item[0], TestProtocol)

    def test_protocol_conflicts(self):
        global TestProtocol, TestProtocol1

        @ptah.sockjs.protocol('test')
        class TestProtocol(ptah.sockjs.Protocol):
            pass

        @ptah.sockjs.protocol('test')
        class TestProtocol1(ptah.sockjs.Protocol):
            pass

        self.config.scan(self.__class__.__module__)
        self.assertRaises(ConfigurationConflictError, self.config.commit)

    def test_protocol_permission(self):
        global TestProtocol
        @ptah.sockjs.protocol('test', permission='ManageSettings')
        class TestProtocol(ptah.sockjs.Protocol):
            pass

        self.config.scan(self.__class__.__module__)
        self.config.commit()

        from ptah.sockjs.session import IProtocol, Session
        item = self.config.registry.adapters.lookup(
            (implementedBy(Session),), IProtocol, name='test')

        self.assertEqual(item[1], 'ManageSettings')

    def test_protocol_custom_session(self):
        class CustomSession(object):pass

        global TestProtocol
        @ptah.sockjs.protocol('test-custom', CustomSession)
        class TestProtocol(ptah.sockjs.Protocol):
            pass

        self.config.scan(self.__class__.__module__)
        self.config.commit()

        from ptah.sockjs.session import IProtocol, Session

        item = self.config.registry.adapters.lookup(
            (implementedBy(Session),), IProtocol, name='test-custom')

        self.assertIsNone(item)

        item = self.config.registry.adapters.lookup(
            (implementedBy(CustomSession),), IProtocol, name='test-custom')

        self.assertIs(item[0], TestProtocol)


@unittest.skipUnless(has_sockjs, 'No pyramid_sockjs')
class TestHandlerDirective(ptah.PtahTestCase):

    def test_handler(self):
        @ptah.sockjs.protocol('test')
        class TestProtocol(object):

            @ptah.sockjs.handler('message')
            def msg_message(self, data):
                """ """

        self.assertTrue(hasattr(TestProtocol, '__handlers__'))
        self.assertIn('message', TestProtocol.__handlers__)
        self.assertEqual('msg_message', TestProtocol.__handlers__['message'])

    def test_external_function_handler(self):
        @ptah.sockjs.protocol('test')
        class TestProtocol(object):
            pass

        @ptah.sockjs.handler('message', TestProtocol)
        def msg_message(self, type, payload, proto):
            """ """

        self.assertTrue(hasattr(TestProtocol, '__handlers__'))
        self.assertIn('message', TestProtocol.__handlers__)
        self.assertEqual(msg_message, TestProtocol.__handlers__['message'])

    def test_external_object_handler(self):
        @ptah.sockjs.protocol('test')
        class TestProtocol(object):
            pass

        @ptah.sockjs.handler('message', TestProtocol)
        class MessageHandler(object):
            """ """

        self.assertTrue(hasattr(TestProtocol, '__handlers__'))
        self.assertIn('message', TestProtocol.__handlers__)
        self.assertEqual(MessageHandler, TestProtocol.__handlers__['message'])


@unittest.skipUnless(has_sockjs, 'No pyramid_sockjs')
class TestProtocol(ptah.PtahTestCase):

    def _make_one(self, id='session'):
        s = ptah.sockjs.Session(id)
        s.request = self.request
        s.registry = self.registry
        return s

    def test_protocol_ctor(self):
        session = self._make_one()
        storage = {}

        protocol = ptah.sockjs.Protocol(session, storage)

        self.assertEqual(protocol.id, session.id)
        self.assertIs(protocol.request, session.request)
        self.assertIs(protocol.registry, session.registry)
        self.assertIs(protocol.storage, storage)
        self.assertIn('__instances__', storage)
        self.assertIs(protocol.instances, storage['__instances__'])

    def test_protocol_open_close(self):
        session = self._make_one()
        storage = {}

        protocol = ptah.sockjs.Protocol(session, storage)
        protocol.on_open()

        self.assertIs(protocol, storage['__instances__'][session.id])

        protocol.on_closed()
        self.assertNotIn(protocol.id, storage['__instances__'])

    def test_protocol_broadcast(self):
        s1 = self._make_one('s1')
        s2 = self._make_one('s2')
        storage = {}

        p1 = ptah.sockjs.Protocol(s1, storage)
        p1.on_open()
        p2 = ptah.sockjs.Protocol(s2, storage)
        p2.on_open()

        data = []
        def send(t, d):
            data.append(t)

        p1.send = send
        p2.send = send

        p1.broadcast('test', {})

        self.assertEqual(len(data), 2)
        data[:] = []

        p2.on_closed()
        p1.broadcast('test', {})
        self.assertEqual(len(data), 1)
        data[:] = []

        p1.session.expired = True
        p1.broadcast('test', {})
        self.assertEqual(len(data), 0)

    def test_protocol_send(self):
        s1 = self._make_one('s1')
        storage = {}

        p1 = ptah.sockjs.Protocol(s1, storage)
        p1.__name__ = 'test'

        data = []
        def send(pr, tp, d):
            data.append((pr, tp, d))

        s1.send = send

        p1.send('message', {})
        self.assertEqual(data[0], ('test', 'message', {}))

        data[:] = []

        p1.__name__ = 'proto1'
        p1.send('message', {})
        self.assertEqual(data[0], ('proto1', 'message', {}))

    def test_dispatch_to_method(self):
        s1 = self._make_one('s1')
        storage = {}
        gdata = []

        class Protocol(ptah.sockjs.Protocol):

            def msg_message(self, data):
                gdata.append(('msg_message', data))

        p = Protocol(s1, storage)

        p.dispatch('message', {}, None)
        self.assertEqual(len(gdata), 1)
        self.assertEqual(gdata[0], ('msg_message', {}))

    def test_dispatch_to_method_exc(self):
        s1 = self._make_one('s1')
        storage = {}
        gdata = []

        class Protocol(ptah.sockjs.Protocol):

            def msg_message(self, data):
                gdata.append(('msg_message', data))
                raise ValueError

        p = Protocol(s1, storage)

        p.dispatch('message', {}, None)
        self.assertEqual(len(gdata), 1)
        self.assertEqual(gdata[0], ('msg_message', {}))

    def test_dispatch_to_named_method(self):
        s1 = self._make_one('s1')
        storage = {}
        gdata = []

        class Protocol(ptah.sockjs.Protocol):

            @ptah.sockjs.handler('test message')
            def msg_message(self, data):
                gdata.append(('test message', data))

        p = Protocol(s1, storage)

        p.dispatch('test message', {}, None)
        self.assertEqual(len(gdata), 1)
        self.assertEqual(gdata[0], ('test message', {}))

    def test_dispatch_to_named_method_exc(self):
        s1 = self._make_one('s1')
        storage = {}
        gdata = []

        class Protocol(ptah.sockjs.Protocol):

            @ptah.sockjs.handler('test message')
            def msg_message(self, data):
                gdata.append(('test message', data))
                raise ValueError

        p = Protocol(s1, storage)

        p.dispatch('test message', {}, None)
        self.assertEqual(len(gdata), 1)
        self.assertEqual(gdata[0], ('test message', {}))

    def test_dispatch_to_external_function(self):
        s1 = self._make_one('s1')
        storage = {}
        gdata = []

        class Protocol(ptah.sockjs.Protocol):
            """ """

        @ptah.sockjs.handler('test message', Protocol)
        def msg_message(tb, data, msg):
            gdata.append(('test message', data))
            raise ValueError

        p = Protocol(s1, storage)

        p.dispatch('test message', {}, None)
        self.assertEqual(len(gdata), 1)
        self.assertEqual(gdata[0], ('test message', {}))

    def test_dispatch_to_external_class(self):
        s1 = self._make_one('s1')
        storage = {}
        gdata = []

        class Protocol(ptah.sockjs.Protocol):
            """ """

        @ptah.sockjs.handler('test message', Protocol)
        class Handler(object):

            def __init__(self, tb, data, msg):
                self.data = data

            def __call__(self):
                gdata.append(('test message', self.data))
                raise ValueError

        p = Protocol(s1, storage)

        p.dispatch('test message', {}, None)
        self.assertEqual(len(gdata), 1)
        self.assertEqual(gdata[0], ('test message', {}))

    def test_dispatch_unknown(self):
        s1 = self._make_one('s1')
        storage = {}
        gdata = []

        class Protocol(ptah.sockjs.Protocol):
            """ """

        p = Protocol(s1, storage)
        p.dispatch('test message', {}, None)
        self.assertEqual(len(gdata), 0)
