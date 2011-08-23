""" directives """
import sys, inspect, imp, logging
from pkgutil import walk_packages
from zope.interface import implementedBy
from zope.component import getSiteManager

log = logging.getLogger('memphis.config')


def action(func):
    info = DirectiveInfo(allowed_scope=('module', 'function call'))
    info.attach(Action(func))
    return func


def adapter(*required, **kw):
    info = DirectiveInfo(allowed_scope=('module', 'function call'))

    required = tuple(required)
    name = kw.get('name', '')

    def wrapper(func):
        info.attach(
            Action(
                _register,
                ('registerAdapter', func, required), {'name': name},
                discriminator = ('memphis.config:adapter', 
                                 required, _getProvides(func), name))
            )
        return func
    return wrapper


def adapts(*required, **kw):
    info = DirectiveInfo(allowed_scope=('class',))

    required = tuple(required)
    name = kw.get('name', '')

    def descriminator(action):
        return ('memphis.config:adapter', 
                required, _getProvides(action.info.context), name)

    info.attach(
        ClassAction(
            _adapts, (required, name),
            discriminator = descriminator)
        )


def utility(provides, name=''):
    info = DirectiveInfo(allowed_scope=('class',))

    info.attach(
        ClassAction(
            _utility,
            (provides, name),
            discriminator = ('memphis.config:utility', provides, name))
        )


def handler(*required):
    info = DirectiveInfo(allowed_scope=('module', 'function call'))

    def wrapper(func):
        info.attach(
            Action(
                _register, ('registerHandler', func, required),
                discriminator = ('memphis.config:handler',func,tuple(required)))
            )
        return func
    return wrapper


def _register(methodName, *args, **kw):
    method = getattr(getSiteManager(), methodName)
    method(*args, **kw)


def _utility(factory, provides, name):
    getSiteManager().registerUtility(factory(), provides, name)


def _adapts(factory, required, name):
    getSiteManager().registerAdapter(factory, required, name=name)


def _getProvides(factory):
    provides = None
    p = list(implementedBy(factory))
    if len(p) == 1:
        return p[0]
    else:
        raise TypeError(
            "The adapter factory doesn't implement a single interface "
            "and no provided interface was specified.")


ATTACH_ATTR = '__memphis_callbacks__'


class Action(object):

    def __init__(self, callable, args=(), kw={}, 
                 discriminator=None, order=0, info=None):
        self.callable = callable
        self.args = args
        self.kw = kw
        self.order = order
        self.info = info
        self._discriminator = discriminator

    @property
    def discriminator(self):
        if callable(self._discriminator):
            return self._discriminator(self)
        return self._discriminator

    def __call__(self):
        self.callable(*self.args, **self.kw)


class ClassAction(Action):

    def __call__(self):
        self.callable(self.info.context, *self.args, **self.kw)


class DirectiveInfo(object):

    def __init__(self, depth=1, moduleLevel = False, allowed_scope=None):
        scope, module, f_locals, f_globals, codeinfo = \
            getFrameInfo(sys._getframe(depth+1))

        if allowed_scope and scope not in allowed_scope:
            raise TypeError("This directive is not allowed "
                            "to run in this scope: %s"%scope)    

        if scope == 'module':
            self.name = f_locals['__name__']
        else:
            self.name = codeinfo[2]

        self.scope = scope
        self.module = module
        self.codeinfo = codeinfo

    @property
    def context(self):
        if self.scope == 'module':
            return self.module
        else:
            return getattr(self.module, self.name)

    def attach(self, action):
        action.info = self
        info = getattr(self.module, ATTACH_ATTR, None)
        if info is None:
            info = []
            setattr(self.module, ATTACH_ATTR, info)

        info.append(action)


def getFrameInfo(frame):
    """Return (kind,module,locals,globals) for a frame
                 
    'kind' is one of "exec", "module", "class", "function call", or "unknown".
    """

    f_locals = frame.f_locals
    f_globals = frame.f_globals
    
    sameNamespace = f_locals is f_globals
    hasModule = '__module__' in f_locals
    hasName = '__name__' in f_globals

    sameName = hasModule and hasName
    sameName = sameName and f_globals['__name__']==f_locals['__module__']

    module = hasName and sys.modules.get(f_globals['__name__']) or None

    namespaceIsModule = module and module.__dict__ is f_globals

    frameinfo = inspect.getframeinfo(frame)
    try:
        sourceline = frameinfo[3][0].strip()
    except: # pragma: no cover
        sourceline = frameinfo[3]

    codeinfo = frameinfo[0], frameinfo[1], frameinfo[2], sourceline

    if not namespaceIsModule: # pragma: no cover
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
    if isinstance(package, basestring):
        try:
            __import__(package)
            package = sys.modules[package]
        except Exception, e:
            log.exception("Can't load package '%s' with exception: %s"%(
                    package, str(e)))
            return ()

    actions = []
    
    pkgname = package.__name__
    if package.__name__ in seen:
        return actions

    seen.add(package.__name__)

    if hasattr(package, ATTACH_ATTR):
        actions.extend(getattr(package, ATTACH_ATTR))

    if hasattr(package, '__path__'): # package, not module
        results = walk_packages(package.__path__, package.__name__+'.')

        for importer, modname, ispkg in results:
            if modname in seen:
                continue

            loader = importer.find_module(modname)
            if loader is not None:
                module_type = loader.etc[2]
                if module_type in (imp.PY_SOURCE, imp.PKG_DIRECTORY):
                    seen.add(modname)
                    if exclude_filter is not None and modname != pkgname:
                        if not exclude_filter(modname):
                            continue

                    try:
                        __import__(modname)
                    except Exception, e:
                        log.exception("Can't load module '%s': %s"%(
                                modname, str(e)))
                        continue

                    module = sys.modules[modname]
                    if hasattr(module, ATTACH_ATTR):
                        actions.extend(getattr(module, ATTACH_ATTR))

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
        if discriminator is None or action.info is None:
            # The discriminator is None or DirectiveInfo is None, 
            # so this directive can never conflict. We can add it 
            # directly to the configuration actions.
            output.append((order, action))
            continue

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
        for includepath, i, action in dups[1:]:
            if discriminator not in conflicts:
                conflicts[discriminator] = [action.info]
            conflicts[discriminator].append(action.info)

    if conflicts:
        raise ConflictError(conflicts)

    # Now put the output back in the original order, and return it:
    r = []
    output.sort()
    for order, action in output:
        r.append(action)

    return r


class ConflictError(TypeError):

    def __init__(self, conflicts):
        self._conflicts = conflicts

    def __str__(self):
        r = ["Conflicting configuration actions\n"]
        items = self._conflicts.items()
        items.sort()
        for discriminator, infos in items:
            r.append("  For: %s\n" % (discriminator, ))
            for info in infos:
                filename, line, function, source = info.codeinfo
                s = ' File "%s", line %d, in %s\n' \
                    '      %s\n'% (filename, line, function, source)

                for line in unicode(s).rstrip().split(u'\n'):
                    r.append(u"    "+line)
                r.append(u'')

        return "\n".join(r)
