""" resource library """
from pyramid.compat import string_types, urlparse

from ptah import config
from ptah.view.resources import static_url

LIBRARY_ID = 'ptah.view:library'


def library(name,
            path='', resource='', type='',
            require='', prefix='', postfix='', extra=None):
    """
    Registers a library with one or more assets.  Used to logically group
    JS and CSS collections.  Provides ability to declarare dependency/requirements
    between library collections.

    :param name: Library collection name
    :param path: A relative file path or tuple of relative paths for the library. 
                 If not relative to a view.static resource name must be absolute url.
    :param resource: A view.static registration name
    :param type:  A string, either `css` or `js`
    :param require: A library name to be considered dependency (Optional)
    :param prefix: A string which will be generated before the library HTML
    :param postfix: A string which will be generated after the library HTML
                    An example of prefix/postfix is <!-- JS/CSS --> 
    :param extra: Additional attributes for computed library tag 
                  An example of extra is {'type':'text/pythonscript'}
    """
    if not path:
        raise ValueError("path is required")

    if type not in ('js', 'css'):
        raise ValueError("Uknown type '%s'"%type)

    if isinstance(path, string_types):
        path = (path,)

    if require and isinstance(require, string_types):
        require = (require,)

    if not resource:
        for p in path:
            if not urlparse.urlparse(p)[0]:
                raise ValueError("If resource is not defined "
                                 "path has to be absolute url")

    discr = (LIBRARY_ID, name, tuple(path), resource)
    intr = config.Introspectable(LIBRARY_ID, discr, name, LIBRARY_ID)
    intr['name'] = name
    intr['path'] = path
    intr['resource'] = resource
    intr['type'] = type
    intr['require'] = require
    intr['prefix'] = prefix
    intr['postfix'] = postfix
    intr['extra'] = extra

    info = config.DirectiveInfo()
    info.attach(
        config.Action(
            library_impl,
            (name, path, resource, type,
             require, prefix, postfix, extra),
            discriminator=discr, introspectables=(intr,))
        )


def library_impl(cfg, name, path, resource, type,
                 require, prefix, postfix, extra):
    data = cfg.get_cfg_storage(LIBRARY_ID)

    lib = data.get(name)
    if lib is None:
        lib = Library(name)
        data[name] = lib

    if extra is None:
        extra = {}

    if path:
        lib.add(path, resource, type, require, prefix, postfix, extra)


def include(request, name):
    """
    Given a library name; the library will be attached to the request.
    See render_includes function to compute the HTML from attached libraries.
    
    :param request: Pyramid request
    :param name: Name of library to include
    """
    libs = getattr(request, '__includes', None)
    if libs is None:
        libs = []

    libs.append(name)
    request.__includes = libs


def render_includes(request):
    """
    Renders HTML for all included libraries for this request.

    :param request: Pyramid request
    """
    _libraries = config.get_cfg_storage(LIBRARY_ID)

    seen = set()
    libraries = []

    libs = getattr(request, '__includes', None)
    if libs is None:
        return ''

    def _process(l_id):
        lib = _libraries.get(l_id)
        if lib is None:
            seen.add(l_id)
            return

        for require in lib.require:
            if require not in seen:
                _process(require)

        seen.add(l_id)
        libraries.append(lib)

    for id in libs:
        if id not in seen:
            _process(id)

    return '\n'.join(lib.render(request) for lib in libraries)


class Entry(object):

    def __init__(self, path, resource='',
                 type='', prefix='', postfix='', extra={}):
        self.resource = resource
        self.type = type
        self.prefix = prefix
        self.postfix = postfix

        if type == 'css':
            if 'rel' not in extra:
                extra['rel'] = 'stylesheet'
            if 'type' not in extra:
                extra['type'] = 'text/css'

        self.extra = extra

        self.urls = urls = []
        self.paths = paths = []
        for p in path:
            if urlparse.urlparse(p)[0]:
                urls.append(p)
            else:
                paths.append(p)

    def render(self, request):
        urls = list(self.urls)

        for path in self.paths:
            urls.append(static_url(request, self.resource, path))

        if self.type == 'css':
            s = '<link %shref="%s" />'
        else:
            s = '<script %ssrc="%s"> </script>'

        extra = ' '.join('%s="%s"'%(k,v) for k, v in self.extra.items())
        if extra:
            extra = '%s '%extra

        return '%s%s%s'%(
            self.prefix, '\n\n\t'.join(s%(extra, url) for url in urls),
            self.postfix)


class Library(object):

    def __init__(self, name):
        self.name = name
        self.require = []
        self.entries = []

    def add(self, path, resource, type, require, prefix, postfix, extra):
        self.entries.append(Entry(path,resource,type,prefix,postfix,extra))

        for req in require:
            if req not in self.require:
                self.require.append(req)

    def render(self, request):
        return '\n'.join(entry.render(request) for entry in self.entries)

    def __repr__(self):
        return '<ptah.view.library.Library "%s">'%self.name
