import sys, pkg_resources
from memphis.config import directives
from zope.interface.registry import Components
from zope.interface.interface import adapter_hooks
from zope.interface.interfaces import IObjectEvent

mods = set()


class StopException(Exception):
    """ Special initialization exception means stop execution """

    def __init__(self, exc=None):
        self.exc = exc

    def __str__(self):
        return str(self.exc)


class ApplicationStarting(object):
    """ Memphis sends this event when application is ready to start. """
    directives.event('Application starting event')

    config = None

    def __init__(self, config):
        self.config = config


def initialize(packages=None, excludes=(), reg=None):
    """ Load memphis packages, scan and execute all configuration
    directives. """

    if reg is None:
        reg = Components('memphis')
        reg.registerHandler(objectEventNotify, (IObjectEvent,))

    sys.modules['memphis.config'].registry = reg
    sys.modules['memphis.config.api'].registry = reg

    def exclude_filter(modname):
        if modname in packages:
            return True
        return exclude(modname, excludes)

    # list all packages
    if packages is None:
        packages = loadPackages(excludes=excludes)
        packages.extend([mod for mod in mods if exclude_filter(mod)])
    else:
        packages = loadPackages(packages, excludes=excludes)

    print packages

    # scan packages and load all actions
    seen = set()
    actions = []

    for pkg in packages:
        actions.extend(directives.scan(pkg, seen, exclude_filter))

    # execute actions
    actions = directives.resolveConflicts(actions)
    for action in actions:
        action()


def start(cfg):
    notify(ApplicationStarting(cfg))


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
            if dist.has_metadata('top_level.txt'):
                packages.extend(
                    [p.strip() for p in 
                     dist.get_metadata('top_level.txt').split()])
            else:
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
    """ Send event to event listeners """
    registry.subscribers(event, None)


def objectEventNotify(event):
    registry.subscribers((event.object, event), None)


def adapterHook(iface, obj, name='', default=None):
    return registry.queryAdapter(obj, iface, name, default)

adapter_hooks.append(adapterHook)


_cleanups = set()

def addCleanup(handler):
    _cleanups.add(handler)
    return handler


def cleanUp(*modIds):
    mods.clear()
    
    for h in _cleanups:
        h()

    for modId in modIds:
        if modId in directives.ACTIONS:
            del directives.ACTIONS[modId]
