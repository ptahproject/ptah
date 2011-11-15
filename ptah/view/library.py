""" resource library """
from urlparse import urlparse
from ptah import config
from ptah.view.resources import static_url

LIBRARY_ID = 'ptah.view:library'


def library(name,
            path='', resource='', type='',
            require='', prefix='', postfix='', extra=None):

    if not path:
        raise ValueError("path is required")

    if type not in ('js', 'css'):
        raise ValueError("Uknown type '%s'"%type)

    if isinstance(path, basestring):
        path = (path,)

    if require and isinstance(require, basestring):
        require = (require,)

    if not resource:
        for p in path:
            if not urlparse(p)[0]:
                raise ValueError("If resource is not defined "
                                 "path has to be absolute url")

    info = config.DirectiveInfo()

    info.attach(
        config.Action(
            library_impl,
            (name, path, resource, type,
             require, prefix, postfix, extra),
            discriminator = (LIBRARY_ID, name, tuple(path), resource))
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
    libs = getattr(request, '__includes', None)
    if libs is None:
        libs = []

    libs.append(name)
    request.__includes = libs


def render_includes(request):
    _libraries = config.get_cfg_storage(LIBRARY_ID)

    seen = set()
    libraries = []

    libs = getattr(request, '__includes', None)
    if libs is None:
        return u''

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

    return u'\n'.join(lib.render(request) for lib in libraries)


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
            if urlparse(p)[0]:
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
