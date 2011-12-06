import re
import os
import pkg_resources
from pyramid.path import caller_package
from chameleon.zpt.template import PageTemplateFile
from chameleon.zpt.template import PageTextTemplateFile
from ptah import config

import ast
from chameleon import nodes
from chameleon.astutil import Builtin
from chameleon.zpt.program import MacroProgram


class PageTemplateFile(PageTemplateFile): # pragma: no cover

    def parse(self, body):
        if self.literal_false:
            default_marker = ast.Str(s="__default__")
        else:
            default_marker = Builtin("False")

        return MacroProgram(
            body, self.mode, self.filename,
            escape=True if self.mode == "xml" else False,
            default_marker=default_marker,
            boolean_attributes=self.boolean_attributes,
            implicit_i18n_translate=self.implicit_i18n_translate,
            implicit_i18n_attributes=self.implicit_i18n_attributes,
            )


class MacroProgram(MacroProgram): # pragma: no cover

    def visit_text(self, node):
        self._last = node
        translation = self.implicit_i18n_translate

        if self._interpolation[-1] and '${' in node:
            return nodes.Interpolation(
                nodes.Substitution(node, ()), False, translation)

        if not translation:
            return nodes.Text(node)

        seq = []
        while node:
            m = re.search('\s+', node)
            if m is not None:
                s = m.start()
                if s:
                    t = node[:s]
                    seq.append(nodes.Translate(t, nodes.Text(t)))

                e = m.end()
                whitespace = nodes.Text(node[s:e])
                seq.append(whitespace)

                if e < len(node):
                    node = node[e:]
                    continue
            else:
                seq.append(nodes.Translate(node, nodes.Text(node)))
            break

        return nodes.Sequence(seq)


registry = {}

class _Template(object):

    def __init__(self, default, custom=None, spec=''):
        self.default = default
        self.custom = custom
        self.spec = spec

        self.tmpl = default

    def setCustom(self, custom): # pragma: no cover
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


def template(spec, layer=None, title=None, description=None, nolayer=False):
    abspath, package_name = path(spec, caller_package(2).__name__)
    if not abspath:
        raise ValueError('Missing template asset: %s' % spec)

    if not nolayer:
        if layer is None:
            layer = package_name

        data = registry.setdefault(layer, {})

        filename = os.path.split(abspath)[1]

        if filename in data:
            tmpl = data[filename][3]
        else:
            tmpl = _Template(getRenderer(abspath), spec=spec)
            data[filename] = [abspath,title,description,tmpl,package_name]
    else:
        tmpl = _Template(getRenderer(abspath), spec=spec)

    return tmpl


def getRenderer(path):
    if path.endswith('.txt'):
        return PageTextTemplateFile(path)

    return PageTemplateFile(path)


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


@config.cleanup
def cleanup():
    registry.clear()
