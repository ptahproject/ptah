import pkg_resources
from pyramid.path import caller_package, caller_module
from chameleon.zpt.template import PageTemplateFile

def template(spec, abs=False):
    try:
        package_name, filename = spec.split(':', 1)
    except ValueError:
        # somehow we were passed a relative pathname
        package_name = caller_package(2).__name__
        filename = spec

    if not abs:
        abspath = pkg_resources.resource_filename(package_name, filename)
        if not pkg_resources.resource_exists(package_name, filename):
            raise ValueError('Missing template asset: %s (%s)' % (spec,abspath))
    else:
        abspath = spec

    return PageTemplateFile(abspath)
