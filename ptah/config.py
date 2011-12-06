import sys
import imp
import inspect
import logging
import signal
import traceback
import pkg_resources
from collections import defaultdict, OrderedDict
from pkgutil import walk_packages
from pyramid.compat import text_type, string_types, NativeIO
from pyramid.threadlocal import get_current_registry
from zope.interface import implementedBy
from zope.interface.interfaces import IObjectEvent

__all__ = ('initialize', 'get_cfg_storage', 'StopException',
           'list_packages', 'cleanup', 'cleanup_system',
           'event', 'adapter', 'subscriber',
           'Action', 'ClassAction', 'DirectiveInfo',
           'ConflictError', 'LayerWrapper',
           'shutdown', 'shutdown_handler')


log = logging.getLogger('ptah')

mods = set()

import ptah


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


def initialize(config, packages=None, excludes=(),
               autoinclude=False, initsettings=True):
    """ Load ptah packages, scan and execute all configuration directives. """
    registry = config.registry
    registry.registerHandler(objectEventNotify, (IObjectEvent,))

    def exclude_filter(modname):
        if modname in packages:
            return True
        return exclude(modname, excludes)

    # list all packages
    if autoinclude:
        if packages is None:
            packages = list_packages(excludes=excludes)
            packages.extend([mod for mod in mods if exclude_filter(mod)])
        else:
            packages = list_packages(packages, excludes=excludes)
    elif packages is None:
        packages = ()

    # scan packages and load actions
    seen = set()
    actions = []

    for pkg in packages:
        actions.extend(scan(pkg, seen, exclude_filter))

    # execute actions
    actions = resolveConflicts(actions)

    def runaction(action, cfg):
        cfg.__ptah_action__ = action
        action(cfg)

    for action in actions:
        config.action(action.discriminator, runaction, (action, config))

    config.action(None, registry.notify, (ptah.events.Initialized(config),))

    if initsettings:
        config.action(
            None, ptah.settings.initialize_settings,
            (config, config.registry.settings))


def get_cfg_storage(id, registry=None, default_factory=OrderedDict):
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


def get_cfg_storage_imp(config, id):
    return get_cfg_storage(id, config.registry)


def exclude(modname, excludes=()):
    for n in ('.test', '.ftest'):
        if n in modname:
            return False

    for mod in excludes:
        if modname == mod or modname.startswith(mod):
            return False
    return True


def load_package(name, seen, first=True):
    packages = []

    if name in seen:
        return packages

    seen.add(name)

    try:
        dist = pkg_resources.get_distribution(name)
        for req in dist.requires():
            pkg = req.project_name
            if pkg in seen:
                continue
            packages.extend(load_package(pkg, seen, False))

        distmap = pkg_resources.get_entry_map(dist, 'ptah')
        ep = distmap.get('package')
        if ep is not None:
            if dist.has_metadata('top_level.txt'):
                packages.extend(
                    [p.strip() for p in
                     dist.get_metadata('top_level.txt').split()])
    except pkg_resources.DistributionNotFound:
        pass

    if first and name not in packages and '-' not in name:
        packages.append(name)

    return packages


def list_packages(include_packages=None, excludes=None):
    seen = set()
    packages = []

    if include_packages is not None:
        for pkg in include_packages:
            if excludes and pkg in excludes:
                continue
            packages.extend(load_package(pkg, seen))
    else:
        for dist in pkg_resources.working_set:
            pkg = dist.project_name
            if pkg in seen:
                continue
            if excludes and pkg in excludes:
                continue

            distmap = pkg_resources.get_entry_map(dist, 'ptah')
            if 'package' in distmap:
                packages.extend(load_package(pkg, seen))
            else:
                seen.add(pkg)

    return packages


def objectEventNotify(event):
    get_current_registry().subscribers((event.object, event), None)


_cleanups = set()


def cleanup(handler):
    _cleanups.add(handler)
    return handler


def cleanup_system(*modIds):
    mods.clear()

    for h in _cleanups:
        h()

    for modId in modIds:
        mod = sys.modules[modId]
        if hasattr(mod, ATTACH_ATTR):
            delattr(mod, ATTACH_ATTR)


class EventDescriptor(object):

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


EVENT_ID = 'ptah.config:event'


def event(title='', category=''):
    """ Register event object, it is used for introspection only. """
    info = DirectiveInfo(allowed_scope=('class',))

    def descriminator(action):
        return (EVENT_ID, action.info.context)

    info.attach(
        ClassAction(
            _event, (title, category),
            discriminator=descriminator)
        )


def _event(cfg, klass, title, category):
    storage = cfg.get_cfg_storage(EVENT_ID)
    ev = EventDescriptor(klass, title, category)
    storage[klass] = ev
    storage[ev.name] = ev


def adapter(*required, **kw):
    """ Register adapter """
    info = DirectiveInfo()

    required = tuple(required)
    name = kw.get('name', '')

    def descriminator(action):
        return ('ptah.config:adapter',
                required, _getProvides(action.info.context), name)

    if info.scope in ('module', 'function call'):  # function decorator
        def wrapper(func):
            info.attach(
                Action(
                    _register,
                    ('registerAdapter', func, required), {'name': name},
                    discriminator=('ptah.config:adapter',
                                   required, _getProvides(func), name))
                )
            return func
        return wrapper
    else:
        info.attach(
            ClassAction(
                _adapts, (required, name),
                discriminator=descriminator)
            )


def subscriber(*required):
    """ Register event subscriber. """
    info = DirectiveInfo(allowed_scope=('module', 'function call'))

    def wrapper(func):
        info.attach(
            Action(
                _register, ('registerHandler', func, required),
                discriminator=('ptah.config:subscriber',
                                func, tuple(required)))
            )
        return func
    return wrapper


def _register(cfg, methodName, *args, **kw):
    method = getattr(cfg.registry, methodName)
    method(*args, **kw)


def _adapts(cfg, factory, required, name):
    cfg.registry.registerAdapter(factory, required, name=name)


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


ATTACH_ATTR = '__ptah_actions__'


class Action(object):

    hash = None

    def __init__(self, callable, args=(), kw={},
                 discriminator=None, order=0, info=None):
        self.callable = callable
        self.args = args
        self.kw = kw
        self.order = order
        self.info = info
        self._discriminator = discriminator

    def __hash__(self):
        return hash(self.hash)

    def __repr__(self):
        return '<%s "%s">'%(self.__class__.__name__, self.discriminator[0])

    @property
    def discriminator(self):
        if callable(self._discriminator):
            return self._discriminator(self)
        return self._discriminator

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
        self.codeinfo = codeinfo

        mods.add(self.module.__name__)

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

    def attach(self, action):
        action.info = self
        if action.hash is None:
            action.hash = self.hash

        data = getattr(self.module, ATTACH_ATTR, None)
        if data is None:
            data = OrderedDict()
            setattr(self.module, ATTACH_ATTR, data)

        if action.hash in data:
            raise TypeError(
                "Directive registered twice: %s" % (action.discriminator,))
        data[action.hash] = action


def getFrameInfo(frame):
    """code from venusian package
    Return (kind,module,locals,globals) for a frame

    'kind' is one of "exec", "module", "class", "function call", or "unknown".
    """

    f_locals = frame.f_locals
    f_globals = frame.f_globals

    sameNamespace = f_locals is f_globals
    hasModule = '__module__' in f_locals
    hasName = '__name__' in f_globals

    sameName = hasModule and hasName
    sameName = sameName and f_globals['__name__'] == f_locals['__module__']

    module = hasName and sys.modules.get(f_globals['__name__']) or None

    namespaceIsModule = module and module.__dict__ is f_globals

    frameinfo = inspect.getframeinfo(frame)
    try:
        sourceline = frameinfo[3][0].strip()
    except:  # pragma: no cover
        sourceline = frameinfo[3]

    codeinfo = frameinfo[0], frameinfo[1], frameinfo[2], sourceline

    if not namespaceIsModule:  # pragma: no cover
        # some kind of funky exec
        kind = "exec"
    elif sameNamespace and not hasModule:
        kind = "module"
    elif sameName and not sameNamespace:
        kind = "class"
    elif not sameNamespace:
        kind = "function call"
    else:  # pragma: no cover
        # How can you have f_locals is f_globals, and have '__module__' set?
        # This is probably module-level code, but with a '__module__' variable.
        kind = "unknown"
    return kind, module, f_locals, f_globals, codeinfo


def scan(package, seen, exclude_filter=None):
    if isinstance(package, string_types):
        __import__(package)
        package = sys.modules[package]

    actions = []

    pkgname = package.__name__
    if pkgname in seen:
        return actions

    seen.add(pkgname)

    if hasattr(package, ATTACH_ATTR):
        actions.extend(getattr(package, ATTACH_ATTR).values())

    if hasattr(package, '__path__'):  # package, not module
        results = walk_packages(package.__path__, package.__name__ + '.')

        for importer, modname, ispkg in results:
            if modname in seen:  # pragma: no cover
                continue

            seen.add(modname)

            if exclude_filter is not None and modname != pkgname:
                if not exclude_filter(modname):
                    continue

            loader = importer.find_module(modname)
            if loader is not None:
                module_type = loader.etc[2]
                if module_type in (imp.PY_SOURCE, imp.PKG_DIRECTORY):
                    __import__(modname)
                    module = sys.modules[modname]
                    if hasattr(module, ATTACH_ATTR):
                        actions.extend(getattr(module, ATTACH_ATTR).values())

    return actions


def resolveConflicts(actions):
    # code from zope.configuration package

    # organize actions by discriminators
    unique = {}
    output = []
    for i in range(len(actions)):
        action = actions[i]
        discriminator = action.discriminator

        order = action.order or i
        a = unique.setdefault(discriminator, [])
        a.append((action.info.codeinfo[0], order, action))

    # Check for conflicts
    conflicts = {}

    for discriminator, dups in unique.items():
        # We need to sort the actions by the paths so that the shortest
        # path with a given prefix comes first:
        dups.sort()
        basepath, order, action = dups[0]

        output.append((order, action))
        if len(dups) > 1:
            conflicts[discriminator] = [
                action.info for _i1, _i2, action in dups]

    if conflicts:
        raise ConflictError(conflicts)

    # Now put the output back in the original order, and return it:
    r = []
    for order, action in sorted(output, key=lambda x:x[0]):
        r.append(action)

    return r


class ConflictError(TypeError):

    def __init__(self, conflicts):
        self._conflicts = conflicts

    def __str__(self):
        r = ["Conflicting configuration actions\n"]
        items = self._conflicts.items()
        for discriminator, infos in sorted(items):
            r.append("  For: %s\n" % (discriminator, ))
            for info in infos:
                filename, line, function, source = info.codeinfo
                s = ' File "%s", line %d, in %s\n' \
                    '      %s\n' % (filename, line, function, source)

                for line in text_type(s).rstrip().split('\n'):
                    r.append("    " + line)
                r.append('')

        return "\n".join(r)


handlers = []
_handler_int = signal.getsignal(signal.SIGINT)
_handler_term = signal.getsignal(signal.SIGTERM)


def shutdown_handler(handler):
    handlers.append(handler)
    return handler


def shutdown():
    for handler in handlers:
        try:
            handler()
        except:
            log.exception("Showndown handler: %s"%handler)
            pass


def processShutdown(sig, frame):
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
