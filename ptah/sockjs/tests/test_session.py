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
