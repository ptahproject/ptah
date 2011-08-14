""" resource library """
from urlparse import urlparse
from memphis.view.resources import static_url

_libraries = {}


def library(name, 
            path='', resource='', type='', 
            require='', prefix='',postfix=''):
    if type not in ('js', 'css'):
        raise ValueError("Uknown type '%s'"%type)

    lib = _libraries.get(name)
    if lib is None:
        lib = Library(name)
        _libraries[name] = lib

    if path:
        lib.add(path, resource, type, require, prefix, postfix)


def include(name, request):
    libs = getattr(request, '__includes', None)
    if libs is None:
        libs = []

    libs.append(name)
    request.__includes = libs


def renderIncludes(request):
    seen = set()
    libraries = []

    libs = getattr(request, '__includes', None)
    if libs is None:
        return u''

    def _process(l_id):
        if l_id in seen:
            return

        lib = _libraries.get(l_id)
        if lib is None:
            seen.add(l_id)
            return

        for require in lib.require:
            _process(require)

            if l_id in seen:
                return

        seen.add(l_id)
        libraries.append(lib)

    for l_id in libs:
        _process(l_id)

    return u'\n'.join(lib.render(request) for lib in libraries)


class Entry(object):

    def __init__(self, path, resource='', 
                 type='', prefix='', postfix='', extra=''):
        self.resource = resource
        self.type = type
        self.prefix = prefix
        self.postfix = postfix
        self.extra = extra

        if isinstance(path, basestring):
            path = (path,)

        self.urls = urls = []
        self.paths = paths = []
        for p in path:
            if urlparse(p)[0]:
                urls.append(p)
            else:
                paths.append(p)

    def render(self, request):
        result = [self.prefix]
        
        urls = list(self.urls)
        
        for path in self.paths:
            urls.append(static_url(self.resource, path, request))

        if self.type == 'css':
            s = '<link rel="stylesheet" %s href="%s" type="text/css" />'
        else:
            s = '<script %s src="%s"> </script>'

        return '\n\t'.join(s%(self.extra, url) for url in urls)


class Library(object):

    def __init__(self, name):
        self.name = name
        self.require = []
        self.entries = []

    def add(self, path, resource='', type='', 
            require='', prefix='', postfix='', extra=''):
        self.entries.append(Entry(path, resource, type, prefix, postfix, extra))

        if require:
            if isinstance(require, basestring):
                require = (require,)

            for req in require:
                if req not in self.require:
                    self.require.append(req)

    def render(self, request):
        return '\n'.join(entry.render(request) for entry in self.entries)

    def __repr__(self):
        return '<memphis.view.library.Library "%s">'%self.name
