import os, sys, imp, pkg_resources
from pyramid.path import caller_package
from chameleon.zpt.template import PageTemplateFile
from chameleon.zpt.template import PageTextTemplateFile
from memphis.view.formatter import format

registry = {}

class _Template(object):

    def __init__(self, default, custom=None):
        self.default = default
        self.custom = custom

        self.tmpl = default

    def setCustom(self, custom):
        if custom is None:
            self.custom = None
            self.tmpl = self.default
        else:
            self.custom = custom
            self.tmpl = custom

    def __call__(self, *args, **kw):
        return self.tmpl(*args, **kw)

    def __repr__(self):
        return repr(self.tmpl)


def template(spec, title=None, description=None):
    abspath, package_name = path(spec, False, caller_package(2).__name__)
    if not abspath:
        raise ValueError('Missing template asset: %s' % spec)

    data = registry.setdefault(package_name, {})
    filename = os.path.split(abspath)[1]
    if filename in data:
        raise ValueError(
            'Template with this name already has been registered: %s'%filename)

    tmpl = _Template(getRenderer(abspath))

    data[filename] = [abspath,title,description,tmpl]

    return tmpl


def getRenderer(path):
    if path.endswith('.txt'):
        return PageTextTemplateFile(path, extra_builtins={'format': format})

    return PageTemplateFile(path, extra_builtins={'format': format})


def path(spec, abs=False, package_name=None):
    try:
        package_name, filename = spec.split(':', 1)
    except ValueError:
        # somehow we were passed a relative pathname
        if package_name is None:
            package_name = caller_package(2).__name__
        filename = spec

    if not abs:
        abspath = pkg_resources.resource_filename(package_name, filename)
        if not pkg_resources.resource_exists(package_name, filename):
            if os.path.exists(spec):
                return spec, package_name
            return None, package_name
    else:
        abspath = spec

    return abspath, package_name
