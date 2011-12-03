import sys
import traceback
import pkg_resources
from io import BytesIO
from collections import defaultdict, OrderedDict

from ptah.config import directives
from pyramid.threadlocal import get_current_registry
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
        return ('\n{0}'.format(self.print_tb()))

    def print_tb(self):
        if self.isexc and self.exc_value:
            out = BytesIO()
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
        self.registry = config.registry


class Initialized(object):
    """ ptah sends this after ptah.config.initialize """
    directives.event('Ptah config initialized event')

    def __init__(self, config):
        self.config = config


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
        actions.extend(directives.scan(pkg, seen, exclude_filter))

    # execute actions
    actions = directives.resolveConflicts(actions)

    def runaction(action, cfg):
        cfg.__ptah_action__ = action
        action(cfg)

    for action in actions:
        config.action(action.discriminator, runaction, (action, config))

    config.action(None, registry.notify, (Initialized(config),))

    if 0: #initsettings:
        import settings

        config.action(
            None, settings.initialize_settings,
            (config.registry.settings, config))


def get_cfg_storage(id, registry=None):
    if registry is None:
        registry = get_current_registry()

    try:
        storage = registry.__ptah_storage__
    except AttributeError:
        storage = defaultdict(lambda: OrderedDict())
        registry.__ptah_storage__ = storage

    return storage[id]


def get_cfg_storage_imp(config, id):
    return get_cfg_storage(id, config.registry)


def start(cfg):
    cfg.registry.notify(AppStarting(cfg))


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


def notify(*event):
    """ Send event to event listeners """
    get_current_registry().subscribers(event, None)


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
        if hasattr(mod, directives.ATTACH_ATTR):
            delattr(mod, directives.ATTACH_ATTR)
