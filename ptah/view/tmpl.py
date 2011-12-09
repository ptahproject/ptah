import re
import os
import pkg_resources
from pyramid.path import caller_package


def path(spec, package_name=None):
    if os.path.exists(spec):
        return spec, caller_package(3).__name__

    try:
        package_name, filename = spec.split(':', 1)
    except ValueError:
        # somehow we were passed a relative pathname
        if package_name is None:
            package_name = caller_package(2).__name__
        filename = spec

    abspath = pkg_resources.resource_filename(package_name, filename)
    if not pkg_resources.resource_exists(package_name, filename):
        return None, package_name
    return abspath, package_name
