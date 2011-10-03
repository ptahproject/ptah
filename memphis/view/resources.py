""" static resource management api """
import sys, os, re, colander
from urlparse import urljoin, urlparse
from paste import fileapp, request, httpexceptions

from memphis import config
from memphis.view import tmpl
from memphis.view.customize import LayerWrapper


STATIC = config.registerSettings(
    'static',

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
STATIC.isurl = False


registry = {}
dirs = {}

def static(name, path, layer=''):
    abspath, pkg = tmpl.path(path)
    data = registry[name] = [abspath, pkg]

    if not abspath:
        raise ValueError("Can't find path to static resource")

    if not os.path.isdir(abspath):
        raise ValueError("path is not directory")

    discriminator = ('memphis.view:static', name, layer)

    info = config.DirectiveInfo()
    info.attach(
        config.Action(
            LayerWrapper(lambda a1,a2,a3: registry.update({a1: (a2, a3)}),
                         discriminator),
            (name, abspath, pkg),
            discriminator = discriminator))


def static_url(name, path, request, **kw):
    url = STATIC.url

    if STATIC.isurl:
        return '%s/%s/%s'%(url, name, path)
    else:
        rname = '%s-%s'%(url, name)
        url = request.route_url('%s-%s'%(url, name), subpath = path)
        if not path:
            return url[:-1]
        return url


def buildTree(path, not_allowed=re.compile('^[.~$#]')):
    data = {}

    for item in os.listdir(path):
        if not_allowed.match(item):
            continue

        _bp = os.path.join(path, item)
        if os.path.isdir(_bp):
            d = buildTree(os.path.join(path, item), not_allowed)
            for sitem, _t in d.items():
                data[os.path.join(item, sitem)] = 1
        else:
            data[item] = 1

    return data


@config.subscriber(config.SettingsInitializing)
def initialize(ev):
    if ev.config is not None:
        url = STATIC.url
        if urlparse(url)[0]:
            # it's a URL
            STATIC.isurl = True
            for name, data in registry.items():
                dirs[name] = (0, urljoin(url, name))

        else:
            for name, (abspath, pkg) in registry.items():
                prefix = '%s/%s'%(url, name)
                rname = '%s-%s'%(url, name)
                pattern = '%s/*subpath'%prefix

                ev.config.add_route(rname, pattern)
                ev.config.add_view(
                    route_name=rname,
                    view=StaticView(abspath, buildTree(abspath), prefix))


class StaticView(object):

    def __init__(self, path, dirinfo, prefix):
        self.path = path
        self.dirinfo = dirinfo
        self.prefix = '/%s'%prefix
        self.lprefix = len(self.prefix)+1

    def __call__(self, context, request):
        return request.get_response(self.process)

    def process(self, environ, start_response):
        path_info = environ.get('PATH_INFO')
        if not path_info:
            return self.not_found(environ, start_response)

        # windows only
        path = os.path.join(*(path_info[self.lprefix:].split('/')))

        if path in self.dirinfo:
            fa = fileapp.FileApp(os.path.join(self.path, path))
            if STATIC.cache_max_age:
                fa.cache_control(max_age=STATIC.cache_max_age)

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


@config.addCleanup
def cleanup():
    registry.clear()
