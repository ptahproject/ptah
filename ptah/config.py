import sys
import logging
import signal
import traceback
from collections import defaultdict, namedtuple, OrderedDict
from pyramid.compat import text_type, string_types, NativeIO
from pyramid.registry import Introspectable
from pyramid.threadlocal import get_current_registry
from zope.interface import implementedBy
from zope.interface.interfaces import IObjectEvent

import venusian
from venusian.advice import getFrameInfo

ATTACH_ATTR = '__ptah_actions__'
ID_EVENT = 'ptah.config:event'
ID_ADAPTER = 'ptah.config:adapter'
ID_SUBSCRIBER = 'ptah.config:subscriber'

__all__ = ('initialize', 'get_cfg_storage', 'StopException',
           'event', 'adapter', 'subscriber', 'shutdown', 'shutdown_handler',
           'Action', 'ClassAction', 'DirectiveInfo', 'LayerWrapper')

log = logging.getLogger('ptah')


class StopException(Exception):
    """ Special initialization exception means stop execution """

    def __init__(self, exc=None):
        self.exc = exc
        if isinstance(exc, BaseException):
            self.isexc = True
            self.exc_type, self.exc_value, self.exc_traceback = sys.exc_info()
        else:
            self.isexc = False

    def __str__(self):
        return ('\n{0}'.format(self.print_tb()))

    def print_tb(self):
        if self.isexc and self.exc_value:
            out = NativeIO()
            traceback.print_exception(
                self.exc_type, self.exc_value, self.exc_traceback, file=out)
            return out.getvalue()
        else:
            return self.exc


class ObjectEventNotify(object):

    def __init__(self, registry):
        self.registry = registry

    def __call__(self, event):
        self.registry.subscribers((event.object, event), None)


def get_cfg_storage(id, registry=None, default_factory=OrderedDict):
    """ Return current config storage """
    if registry is None:
        registry = get_current_registry()

    try:
        storage = registry.__ptah_storage__
    except AttributeError:
        storage = defaultdict(lambda: OrderedDict())
        registry.__ptah_storage__ = storage

    if id not in storage:
        storage[id] = default_factory()
    return storage[id]


def pyramid_get_cfg_storage(config, id):
    return get_cfg_storage(id, config.registry)


class EventDescriptor(object):
    """ Events descriptor class, it is been used by `event` decorator """

    #: Event name
    name = ''

    #: Event title
    title = ''

    #: Event category
    category = ''

    #: Event class or interface
    instance = None

    def __init__(self, inst, title, category):
        self.instance = inst
        self.title = title
        self.category = category
        self.description = inst.__doc__
        self.name = '%s.%s' % (inst.__module__, inst.__name__)


def event(title='', category=''):
    """ Register event object, it is used for introspection only. """
    info = DirectiveInfo()

    def wrapper(cls):
        discr = (ID_EVENT, cls)

        intr = Introspectable(ID_EVENT, discr, title, ID_EVENT)

        def _event(cfg, klass, title, category):
            storage = cfg.get_cfg_storage(ID_EVENT)
            ev = EventDescriptor(klass, title, category)
            storage[klass] = ev
            storage[ev.name] = ev

            intr['descr'] = ev
            intr['codeinfo'] = info.codeinfo

        info.attach(
            Action(
                _event, (cls, title, category),
                discriminator=discr, introspectables = (intr,))
            )
        return cls

    return wrapper


def adapter(*args, **kw):
    """ Register adapter """
    info = DirectiveInfo()

    required = tuple(args)
    name = kw.get('name', '')

    def wrapper(func):
        discr = (ID_ADAPTER, required, _getProvides(func), name)

        intr = Introspectable(ID_ADAPTER, discr, 'Adapter', ID_ADAPTER)
        intr['name'] = name
        intr['required'] = required
        intr['adapter'] = func
        intr['codeinfo'] = info.codeinfo

        def _register(cfg, name, func, required):
            cfg.registry.registerAdapter(func, required, name=name)

        info.attach(
            Action(
                _register, (name, func, required),
                discriminator = discr, introspectables = (intr,))
            )
        return func

    return wrapper


def subscriber(*args):
    """ Register event subscriber. """
    info = DirectiveInfo(allowed_scope=('module', 'function call'))

    def wrapper(func):
        required = tuple(args)
        discr = (ID_SUBSCRIBER, func, required)

        intr = Introspectable(ID_SUBSCRIBER, discr, 'Subscriber', ID_SUBSCRIBER)
        intr['required'] = required
        intr['handler'] = func
        intr['codeinfo'] = info.codeinfo

        def _register(cfg, func, required):
            cfg.registry.registerHandler(func, required)

        info.attach(
            Action(
                _register, (func, required),
                discriminator=discr, introspectables=(intr,))
            )
        return func

    return wrapper


def _getProvides(factory):
    p = list(implementedBy(factory))
    if len(p) == 1:
        return p[0]
    else:
        raise TypeError(
            "The adapter factory doesn't implement a single interface "
            "and no provided interface was specified.")


class _ViewLayersManager(object):

    def __init__(self):
        self.layers = {}

    def register(self, layer, discriminator):
        data = self.layers.setdefault(discriminator, [])
        if not layer:
            data.insert(0, layer)
        else:
            data.append(layer)

    def enabled(self, layer, discriminator):
        data = self.layers.get(discriminator)
        if data:
            return data[-1] == layer
        return False

_layersManager = _ViewLayersManager()


class LayerWrapper(object):

    def __init__(self, callable, discriminator):
        self.callable = callable
        self.layer = discriminator[-1]
        self.discriminator = discriminator[:-1]
        _layersManager.register(self.layer, self.discriminator)

    def __call__(self, cfg, *args, **kw):
        if not _layersManager.enabled(self.layer, self.discriminator):
            return # pragma: no cover

        self.callable(cfg, *args, **kw)


class Action(object):

    hash = None

    def __init__(self, callable, args=(), kw={},
                 discriminator=None, order=0, introspectables=(), info=None):
        self.callable = callable
        self.args = args
        self.kw = kw
        self.order = order
        self.info = info
        self.introspectables = introspectables
        self.discriminator = discriminator

    def __hash__(self):
        return hash(self.hash)

    def __repr__(self):
        return '<%s "%s">'%(
            self.__class__.__name__,
            self.discriminator[0] if self.discriminator else None)

    def __call__(self, cfg):
        if self.callable:
            try:
                self.callable(cfg, *self.args, **self.kw)
            except:  # pragma: no cover
                log.exception(self.discriminator)
                raise


class ClassAction(Action):

    def __call__(self, cfg):
        try:
            self.callable(cfg, self.info.context, *self.args, **self.kw)
        except:  # pragma: no cover
            log.exception(self.discriminator)
            raise


CodeInfo = namedtuple('Codeinfo', 'filename lineno function source module')


class AttachData(OrderedDict):
    """ container for Attach infos """


class DirectiveInfo(object):

    def __init__(self, depth=1, moduleLevel=False, allowed_scope=None):
        scope, module, f_locals, f_globals, codeinfo = \
            getFrameInfo(sys._getframe(depth + 1))

        if allowed_scope and scope not in allowed_scope:
            raise TypeError("This directive is not allowed "
                            "to run in this scope: %s" % scope)

        if scope == 'module':
            self.name = f_locals['__name__']
        else:
            self.name = codeinfo[2]

        self.locals = f_locals
        self.scope = scope
        self.module = module
        self.codeinfo = CodeInfo(
            codeinfo[0], codeinfo[1], codeinfo[2], codeinfo[3], module.__name__)

        if depth > 1:
            _, mod, _, _, ci = getFrameInfo(sys._getframe(2))
            self.hash = (module.__name__, codeinfo[1], mod.__name__, ci[1])
        else:
            self.hash = (module.__name__, codeinfo[1])

    @property
    def context(self):
        if self.scope == 'module':
            return self.module
        else:
            return getattr(self.module, self.name, None)

    def _runaction(self, action, cfg):
        cfg.__ptah_action__ = action
        action(cfg)

    def attach(self, action):
        action.info = self
        if action.hash is None:
            action.hash = self.hash

        data = getattr(self.module, ATTACH_ATTR, None)
        if data is None:
            data = AttachData()
            setattr(self.module, ATTACH_ATTR, data)

        if action.hash in data:
            raise TypeError(
                "Directive registered twice: %s" % (action.discriminator,))
        data[action.hash] = action

        def callback(context, name, ob):
            config = context.config.with_package(self.module)

            config.info = action.info
            config.action(
                action.discriminator, self._runaction, (action, config),
                introspectables=action.introspectables,
                order=action.order)

        venusian.attach(data, callback, category='ptah')

    def __repr__(self):
        filename, line, function, source, module = self.codeinfo
        return ' File "%s", line %d, in %s\n' \
               '      %s\n' % (filename, line, function, source)


handlers = []
_handler_int = signal.getsignal(signal.SIGINT)
_handler_term = signal.getsignal(signal.SIGTERM)


def shutdown_handler(handler):
    """ register shutdown handler """
    handlers.append(handler)
    return handler


def shutdown():
    """ Execute all registered shutdown handlers """
    for handler in handlers:
        try:
            handler()
        except:
            log.exception("Showndown handler: %s"%handler)
            pass


def processShutdown(sig, frame):
    """ os signal handler """
    shutdown()

    if sig == signal.SIGINT and callable(_handler_int):
        _handler_int(sig, frame)

    if sig == signal.SIGTERM and callable(_handler_term):  # pragma: no cover
        _handler_term(sig, frame)

    if sig == signal.SIGTERM:
        raise sys.exit()

try:
    import mod_wsgi
except ImportError:
    signal.signal(signal.SIGINT, processShutdown)
    signal.signal(signal.SIGTERM, processShutdown)
