from zope.interface import implementedBy
from pyramid.config import Configurator
from pyramid.exceptions import ConfigurationError, ConfigurationConflictError
from pyramid.httpexceptions import HTTPNotFound

import ptah
from ptah.util import json
from ptah.testing import unittest

try:
    import pyramid_sockjs
    has_sockjs = True
except ImportError:
    has_sockjs = False


@unittest.skipUnless(has_sockjs, 'No pyramid_sockjs')
class TestSession(ptah.PtahTestCase):

    def test_get_protocol_unknown(self):
        from ptah.sockjs.session import Session

        s = Session('12345', request=self.request)
        self.assertIsNone(s.get_protocol('unknown'))

    def test_get_protocol_existing(self):
        from ptah.sockjs.session import Session

        s = Session('12345', request=self.request)
        p = object()
        s.protocols['test'] = p

        self.assertIs(s.get_protocol('test'), p)

    def test_get_protocol_create(self):
        from ptah.sockjs.protocol import Protocol
        from ptah.sockjs.session import Session, SessionManager, IProtocol

        class P(Protocol):
            pass

        self.registry.registerAdapter((P, None), (Session,), IProtocol, 'test')

        sm = SessionManager('ptah', self.registry)
        s = sm.get('12345', True, self.request)

        p = s.get_protocol('test')
        self.assertIsInstance(p, P)
        self.assertIs(p.session, s)
        self.assertIs(s.protocols['test'], p)
        self.assertIs(p, s.get_protocol('test'))

    def test_get_protocol_protected(self):
        from ptah.sockjs.protocol import Protocol
        from ptah.sockjs.session import Session, SessionManager, IProtocol

        class P(Protocol):
            pass

        self.registry.registerAdapter((P, 'perm'), (Session,), IProtocol, 'p')

        sm = SessionManager('ptah', self.registry)
        s = sm.get('12345', True, self.request)

        allow = False
        def check_perm(p, c, r):
            return allow

        orig = ptah.check_permission
        ptah.check_permission = check_perm

        p = s.get_protocol('p')
        self.assertIsNone(p)

        allow = True

        # cached
        p = s.get_protocol('p')
        self.assertIsNone(p)

        s = sm.get('12346', True, self.request)
        p = s.get_protocol('p')
        self.assertIsInstance(p, P)

        ptah.check_permission = orig

    def test_shared_storage(self):
        from ptah.sockjs.protocol import Protocol
        from ptah.sockjs.session import Session, SessionManager, IProtocol

        class P(Protocol): pass
        self.registry.registerAdapter((P, None), (Session,), IProtocol, 'p')

        sm = SessionManager('ptah', self.registry)
        s1 = sm.get('12345', True, self.request)
        s2 = sm.get('12346', True, self.request)

        p1 = s1.get_protocol('p')
        p2 = s2.get_protocol('p')

        self.assertIs(p1.storage, p2.storage)
        self.assertIs(sm.storage['p'], p1.storage)

    def test_on_close(self):
        from ptah.sockjs.protocol import Protocol
        from ptah.sockjs.session import Session, SessionManager, IProtocol

        data = {}

        class P(Protocol):
            def on_closed(self):
                data[self.name] = 1
        class P1(P):
            name = 'p1'
        class P2(P):
            name = 'p2'

        self.registry.registerAdapter((P1, None), (Session,), IProtocol, 'p1')
        self.registry.registerAdapter((P2, None), (Session,), IProtocol, 'p2')

        sm = SessionManager('ptah', self.registry)
        s = sm.get('12345', True, self.request)
        s.get_protocol('p1')
        s.get_protocol('p2')
        s.on_closed()

        self.assertIn('p1', data)
        self.assertIn('p2', data)

    def test_on_message(self):
        from ptah.sockjs.protocol import Protocol
        from ptah.sockjs.session import Session, SessionManager, IProtocol

        data = {}

        class P(Protocol):
            def msg_test(self, *args):
                data['test'] = args[0]

        self.registry.registerAdapter((P, None), (Session,), IProtocol, 'p')

        sm = SessionManager('ptah', self.registry)
        s = sm.get('12345', True, self.request)

        s.on_message(json.dumps(
                {'protocol':'p', 'type': 'test', 'payload': {'data': 1}}))

        self.assertIn('test', data)
        self.assertEqual(data['test'], {'data': 1})

    def test_on_message_unknown_protocol(self):
        from ptah.sockjs.session import Session, SessionManager

        sm = SessionManager('ptah', self.registry)
        s = sm.get('12345', True, self.request)

        s.on_message(json.dumps(
                {'protocol':'p', 'type': 'unknown', 'payload': {'data': 1}}))

    def test_send(self):
        from ptah.sockjs.session import Session, SessionManager

        sm = SessionManager('ptah', self.registry)
        s = sm.get('12345', True, self.request)
        s.send('p', 'init', {'data': 1})

        self.assertEqual(
            s.queue.get(),
            {'type': 'init', 'protocol': 'p', 'payload': {'data': 1}})

    def test_broadcast(self):
        from ptah.sockjs.protocol import Protocol
        from ptah.sockjs.session import Session, SessionManager, IProtocol

        class P(Protocol): pass
        self.registry.registerAdapter((P, None), (Session,), IProtocol, 'p')

        sm = SessionManager('ptah', self.registry)
        s1 = sm.get('12345', True, self.request)
        s2 = sm.get('12346', True, self.request)

        p1 = s1.get_protocol('p')
        p2 = s2.get_protocol('p')

        sm.broadcast('p', 'init', {'data': 1})

        self.assertEqual(
            s1.queue.get(),
            {'type': 'init', 'protocol': 'p', 'payload': {'data': 1}})
        self.assertEqual(
            s2.queue.get(),
            {'type': 'init', 'protocol': 'p', 'payload': {'data': 1}})


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

        from ptah.sockjs import get_session_manager
        self.assertIs(
            pyramid_sockjs.get_session_manager('ptah', self.registry),
            get_session_manager(self.registry))
