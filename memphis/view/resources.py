""" static resource management api """
import sys, os, re, colander
from urlparse import urljoin, urlparse
from paste import fileapp, request, httpexceptions

from memphis import config
from memphis.view import tmpl


RESOURCE = config.registerSettings(
    'resource',

    config.SchemaNode(
        colander.Str(),
        name = 'url',
        default = 'static'),

    config.SchemaNode(
        colander.Int(),
        name = 'cache_max_age',
        default = 0),

    title = 'Static resources management',
)


registry = {}


def registerStatic(name, path):
    abspath, pkg = tmpl.path(path)
    if not os.path.isdir(abspath):
        raise ValueError("path is not directory")

    config.action(
        registerStaticImpl,
        name, abspath, pkg,
        __discriminator = ('memphis:registerStatic', name, path),
        __info = config.getInfo(2),
        __frame = sys._getframe(1))


def registerStaticImpl(name, abspath, pkg):
    data = registry.setdefault(name, [])
    data.append((abspath, pkg))


def buildTree(path, not_allowed=re.compile('^[.~$#]')):
    data = {}

    for item in os.listdir(path):
        if not_allowed.match(item):
            continue

        newpath = os.path.join(path, item)
        if os.path.isdir(newpath):
            d = buildTree(newpath, not_allowed)
            if d:
                data[item] = (0, d)
        else:
            data[item] = (1,)

    return data


@config.handler(config.SettingsInitializing)
def initialize(ev):
    if ev.config is None:
        return

    url = RESOURCE.url
    if urlparse(url)[0]:
        # it's a URL
        for name, data in registry.items():
            registry[name] = (0, urljoin(url, name))

    else:
        if not url.endswith('/'):
            url = '%s/'%url

        for name, data in registry.items():
            dirinfo = []
            for abspath, pkg in data:
                dirinfo.insert(0, (abspath, buildTree(abspath)))
            
            prefix = '%s%s'%(url, name)
            registry[name] = (1, prefix)

            rname = '%s-%s'%(url, name)
            pattern = '%s/*subpath'%prefix
            ev.config.add_route(rname, pattern)
            ev.config.add_view(
                route_name=rname, 
                view=StaticView(dirinfo, prefix))


class StaticView(object):

    def __init__(self, data, prefix):
        self.data = data
        self.prefix = '/%s'%prefix
        self.lprefix = len(self.prefix)

    def __call__(self, context, request):
        return request.get_response(self.process)
    
    def process(self, environ, start_response):
        path_info = environ.get('PATH_INFO')

        if not path_info:
            return self.not_found(environ, start_response)

        data = self.data
        path = [s for s in path_info[self.lprefix:].split('/') if s]

        for abspath, dirinfo in data:
            filepath = [abspath]

            found = False
            for item in path:
                if item in dirinfo:
                    filepath.append(item)
                    if dirinfo[item][0] == 1:
                        found = True
                        break
                    else:
                        dirinfo = dirinfo[item][1]

            if found:
                break

            filepath = None

        if filepath:
            fa = fileapp.FileApp(os.path.join(*filepath))
            
            if RESOURCE.cache_max_age:
                fa.cache_control(max_age=RESOURCE.cache_max_age)

            return fa(environ, start_response)

        return self.not_found(environ, start_response)

    def not_found(self, environ, start_response, debug_message=None):
        comment=('SCRIPT_NAME=%r; PATH_INFO=%r; debug: %s' % (
                environ.get('SCRIPT_NAME'),
                environ.get('PATH_INFO'),
                debug_message or '(none)'))
        exc = httpexceptions.HTTPNotFound(
            'The resource at %s could not be found'
            % request.construct_url(environ),
            comment=comment)
        return exc.wsgi_application(environ, start_response)
