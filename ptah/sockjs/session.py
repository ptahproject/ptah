import logging
import ptah
from ptah import config
from zope import interface
from zope.interface import providedBy
from pyramid.decorator import reify
from pyramid.registry import Introspectable

import pyramid_sockjs
from pyramid_sockjs import json

log = logging.getLogger('ptah')


class IProtocol(interface.Interface):
    """ protocol """


class Session(pyramid_sockjs.Session):

    def __init__(self, *args, **kw):
        super(Session, self).__init__(*args, **kw)

        self.protocols = {}

    def get_protocol(self, name, _marker=object()):
        protocol = self.protocols.get(name)

        if protocol is None:
            item = self.registry.adapters.lookup(
                (providedBy(self),), IProtocol, name=name)
            if item is not None:
                factory, permission = item
            else:
                factory, permission = None, None

            # permission
            if permission:
                if not ptah.check_permission(
                    permission, self.request.context, self.request):
                    factory = None
                    self.protocols[name] = component = _marker
                    log.warning("Permission check failed for %s"%name)

            if factory is not None:
                # shared storage
                storage = self.manager.storage.get(name)
                if storage is None:
                    storage = {}
                    self.manager.storage[name] = storage

                # create
                protocol = factory(self, storage)
                protocol.__name__ = name
                protocol.request = self.request
                protocol.on_open()
                self.protocols[name] = protocol

        return protocol if protocol is not _marker else None

    def send(self, protocol, type, payload, **kw):
        kw['protocol'] = protocol
        kw['type'] = type
        kw['payload'] = payload
        super(Session, self).send(kw)

    def on_message(self, raw_msg):
        proto, tp, payload = raw_msg.split('|', 2)

        protocol = self.get_protocol(proto)
        if protocol is not None:
            protocol.dispatch(tp, json.loads(payload))

    def on_closed(self):
        for name, protocol in self.protocols.items():
            if hasattr(protocol, 'on_closed'):
                protocol.on_closed()


class SessionManager(pyramid_sockjs.SessionManager):

    factory = Session

    def __init__(self, *args, **kw):
        super(SessionManager, self).__init__(*args, **kw)

        self.storage = {}

    def broadcast(self, protocol, *args, **kw):
        for session in self.values():
            if not session.expired and protocol in session.protocols:
                session.send(protocol, *args, **kw)


def get_session_manager(registry):
    return pyramid_sockjs.get_session_manager('ptah', registry)
