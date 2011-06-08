import pkg_resources
from pyramid.path import caller_package, caller_module
from chameleon.zpt.template import PageTemplateFile


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
            return None
    else:
        abspath = spec

    return abspath


def template(spec, abs=False):
    abspath = path(spec, abs, caller_package(2).__name__)
    if not abspath:
        raise ValueError('Missing template asset: %s' % spec)

    return PageTemplateFile(abspath)
