import sys, pkg_resources
from memphis.config import directives
from zope.component import getSiteManager


def initialize(packages=None, excludes=()):
    # list all packages
    if packages is None:
        packages = loadPackages()
    else:
        packages = loadPackages(packages)

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


def exclude(modname, excludes):
    for n in ('.test','.ftest'):
        if n in modname:
            return False

    if modname in excludes:
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

    if first and name not in packages:
        packages.append(name)

    return packages


def loadPackages(include_packages=None):
    seen = set()
    packages = []

    if include_packages is not None:
        for pkg in include_packages:
            packages.extend(loadPackage(pkg, seen))
    else:
        for dist in pkg_resources.working_set:
            pkg = dist.project_name
            if pkg in seen:
                continue

            distmap = pkg_resources.get_entry_map(dist, 'memphis')
            if 'package' in distmap:
                packages.extend(loadPackage(pkg, seen))
            else:
                seen.add(pkg)

    return packages


def notify(*event):
    getSiteManager().subscribers(event, None)


_cleanups = set()

def addCleanup(handler):
    _cleanups.add(handler)
    return handler


def cleanUp(modId=None):
    for h in _cleanups:
        h()

    if modId in sys.modules:
        mod = sys.modules[modId]
        if hasattr(mod, directives.ATTACH_ATTR):
            delattr(mod, directives.ATTACH_ATTR)
