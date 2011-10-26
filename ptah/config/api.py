import StringIO
import traceback
import sys, pkg_resources
from collections import defaultdict
from ptah.config import directives
from zope.interface.registry import Components
from zope.interface.interface import adapter_hooks
from zope.interface.interfaces import IObjectEvent

mods = set()


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
        if self.isexc:
            return str(self.exc)
        return self.exc

    def print_tb(self):
        if self.isexc:
            out = StringIO.StringIO()
            traceback.print_exception(
                self.exc_type, self.exc_value, self.exc_traceback, file=out)
            return out.getvalue()
        else:
            return self.exc


class AppStarting(object):
    """ ptah sends this event when application is ready to start. """
    directives.event('Application starting event')

    config = None

    def __init__(self, config):
        self.config = config


class Config(object):

    def __init__(self, registry, actions):
        self.registry = registry
        self.actions = actions
        self.storage = defaultdict(lambda: dict())
        registry.storage = self.storage
        registry.storage['actions'] = actions


def initialize(packages=None, excludes=(), reg=None):
    """ Load ptah packages, scan and execute all configuration
    directives. """

    if reg is None:
        reg = Components('ptah')
        reg.registerHandler(objectEventNotify, (IObjectEvent,))

    sys.modules['ptah.config'].registry = reg
    sys.modules['ptah.config.api'].registry = reg

    def exclude_filter(modname):
        if modname in packages:
            return True
        return exclude(modname, excludes)

    # list all packages
    if packages is None:
        packages = list_packages(excludes=excludes)
        packages.extend([mod for mod in mods if exclude_filter(mod)])
    else:
        packages = list_packages(packages, excludes=excludes)

    # scan packages and load actions
    seen = set()
    actions = []

    for pkg in packages:
        actions.extend(directives.scan(pkg, seen, exclude_filter))

    config = Config(registry, actions)

    # execute actions
    actions = directives.resolveConflicts(actions)

    for action in actions:
        action(config)


def start(cfg):
    notify(AppStarting(cfg))


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
            packages.extend(loadPackage(pkg, seen))
    else:
        for dist in pkg_resources.working_set:
            pkg = dist.project_name
            if pkg in seen:
                continue
            if excludes and pkg in excludes:
                continue

            distmap = pkg_resources.get_entry_map(dist, 'ptah')
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

def cleanup(handler):
    _cleanups.add(handler)
    return handler


def cleanup_system(*modIds):
    mods.clear()
    registry.storage.clear()

    for h in _cleanups:
        h()

    for modId in modIds:
        mod = sys.modules[modId]
        if hasattr(mod, directives.ATTACH_ATTR):
            delattr(mod, directives.ATTACH_ATTR)
