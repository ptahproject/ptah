import logging
import ptah
from ptah import config
from zope.interface import providedBy
from pyramid.registry import Introspectable
from ptah.sockjs.session import IProtocol, Session

ID_PROTOCOL = 'ptah:protocol'

log = logging.getLogger('ptah')


class Protocol(object):

    storage = None
    __name__ = '--unset--'
    __handlers__ = {}

    def __init__(self, session, storage):
        self.id = session.id
        self.session = session
        self.request = session.request
        self.registry = session.registry
        self.storage = storage

        instances = storage.get('__instances__')
        if instances is None:
            storage['__instances__'] = instances = {}

        self.instances = instances

    def on_open(self):
        self.instances[self.id] = self

    def on_closed(self):
        if self.id in self.instances:
            del self.instances[self.id]

    def broadcast(self, *args, **kw):
        for item in self.instances.values():
            if not item.session.expired:
                item.send(*args, **kw)

    def send(self, tp, data, **kw):
        self.session.send(self.__name__, tp, data, **kw)

    def dispatch(self, tp, payload):
        handler = getattr(self, 'msg_%s'%tp, None)
        if handler is not None:
            try:
                handler(payload)
            except Exception as e:
                log.exception("Exception in handler '%s'"%tp)
        else:
            handler = self.__handlers__.get(tp)

            if isinstance(handler, str):
                handler = getattr(self, handler, None)
                if handler is not None:
                    try:
                        handler(payload)
                    except Exception as e:
                        log.exception("Exception in handler '%s'"%tp)

            elif handler is not None:
                try:
                    res = handler(tp, payload, self)
                    if callable(res):
                        res()
                except Exception as e:
                    log.exception("Exception in handler '%s'"%tp)

            else:
                log.warning(
                    "Can't find handler for %s event, protocol %s",
                    tp, self.__name__)


class handler(object):

    def __init__(self, name, context=None):
        self.name = name
        self.context = context

        # method decorator
        if context is None:
            info = config.DirectiveInfo()
            handlers = info.locals.get('__handlers__')
            if handlers is None:
                info.locals['__handlers__'] = handlers = {}
            self.handlers = handlers

    def __call__(self, handler):
        if self.context is None:
            self.handlers[self.name] = handler.__name__
            return handler

        if '__handlers__' not in self.context.__dict__:
            self.context.__handlers__ = {}

        self.context.__handlers__[self.name] = handler

        return handler


class protocol(object):

    def __init__(self, name, session=Session, permission=None):
        self.name = name
        self.session = session
        self.permission = permission

        self.info = config.DirectiveInfo()
        self.discr = (ID_PROTOCOL, name, session)

        self.intr = Introspectable(ID_PROTOCOL, self.discr, name, ID_PROTOCOL)
        self.intr['name'] = name
        self.intr['session'] = session
        self.intr['codeinfo'] = self.info.codeinfo

    def __call__(self, handler, cfg=None):
        intr = self.intr
        intr['handler'] = handler

        self.info.attach(
            config.Action(
                lambda cfg, name, session, permission, handler: \
                cfg.registry.registerAdapter(\
                    (handler, permission), (session,), IProtocol, name),
                (self.name, self.session, self.permission, handler),
                discriminator=self.discr, introspectables=(intr,)),
            cfg)
        return handler
