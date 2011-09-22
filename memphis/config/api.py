import sys, pkg_resources
from memphis.config import directives
from zope.interface.registry import Components
from zope.interface.interfaces import IObjectEvent

registry = Components('memphis')

def _notify(self, *events):
    [ _ for _ in self.subscribers(events, None) ]

def objectEventNotify(event):
    registry.subscribers((event.object, event), None)

registry.registerHandler(objectEventNotify, (IObjectEvent,))


def initialize(packages=None, excludes=(), reg=None):
    global registry
    if reg is not None:
        registry = reg
        if not hasattr(reg, 'notify'):
            reg.notify = _notify
        #reg.registerHandler(objectEventNotify, (IObjectEvent,))

        import memphis.config
        memphis.config.registry = reg

    # list all packages
    if packages is None:
        packages = loadPackages(excludes=excludes)
    else:
        packages = loadPackages(packages, excludes=excludes)

    # scan packages and load all actions
    seen = set()
    actions = []

    def exclude_filter(modname):
        if modname in packages:
            return True
        return exclude(modname, excludes)

    for pkg in packages:
        actions.extend(directives.scan(pkg, seen, exclude_filter))

    # execute actions
    actions = directives.resolveConflicts(actions)
    for action in actions:
        action()


def exclude(modname, excludes=()):
    for n in ('.test','.ftest'):
        if n in modname:
            return False

    for mod in excludes:
        if modname == mod or modname.startswith(mod):
            return False
    return True


def loadPackage(name, seen, first=True):
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
            packages.extend(loadPackage(pkg, seen, False))

        distmap = pkg_resources.get_entry_map(dist, 'memphis')
        ep = distmap.get('package')
        if ep is not None:
            packages.append(ep.module_name)
    except pkg_resources.DistributionNotFound:
        pass

    if first and name not in packages and '-' not in name:
        packages.append(name)

    return packages


def loadPackages(include_packages=None, excludes=None):
    seen = set()
    packages = []

    if include_packages is not None:
        for pkg in include_packages:
            if excludes and pkg in excludes:
                continue
            packages.extend(loadPackage(pkg, seen))
    else:
        for dist in pkg_resources.working_set:
            pkg = dist.project_name
            if pkg in seen:
                continue
            if excludes and pkg in excludes:
                continue

            distmap = pkg_resources.get_entry_map(dist, 'memphis')
            if 'package' in distmap:
                packages.extend(loadPackage(pkg, seen))
            else:
                seen.add(pkg)

    return packages


def notify(*event):
    registry.subscribers(event, None)


_cleanups = set()

def addCleanup(handler):
    _cleanups.add(handler)
    return handler


def cleanUp(*modIds):
    for h in _cleanups:
        h()

    for modId in modIds:
        if modId in sys.modules:
            mod = sys.modules[modId]
            if hasattr(mod, directives.ATTACH_ATTR):
                delattr(mod, directives.ATTACH_ATTR)
