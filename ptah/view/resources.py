""" static resource management api """
import os, re

from pyramid.compat import urlparse
from pyramid.static import _FileResponse
from pyramid.httpexceptions import HTTPNotFound

import ptah
from ptah import config
from ptah.view import tmpl


STATIC_ID = 'ptah.view:static'


def static(name, path, layer=''):
    """ Register new static assets directory

    :param name: Resource name
    :param path: Filesystem path
    """
    abspath, pkg = tmpl.path(path)

    if not abspath:
        raise ValueError("Can't find path to static resource")

    if not os.path.isdir(abspath):
        raise ValueError("path is not directory")

    discriminator = (STATIC_ID, name, layer)

    info = config.DirectiveInfo()
    info.attach(
        config.Action(
            config.LayerWrapper(lambda cfg, a1,a2,a3: \
                         cfg.get_cfg_storage(STATIC_ID)\
                             .update({a1: (a2, a3)}), discriminator),
            (name, abspath, pkg),
            discriminator = discriminator))


def static_url(request, name, path='', **kw):
    cfg = ptah.get_settings(ptah.CFG_ID_PTAH, request.registry)
    url = cfg['static_url']

    if cfg.get('isurl', False):
        return '%s/%s/%s'%(url, name, path)
    else:
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


@config.subscriber(ptah.events.AppStarting)
def initialize(ev):
    cfg = ptah.get_settings(ptah.CFG_ID_PTAH, ev.registry)

    url = cfg['static_url']
    if not urlparse.urlparse(url)[0]:
        registry = config.get_cfg_storage(STATIC_ID)
        for name, (abspath, pkg) in registry.items():
            prefix = '%s/%s'%(url, name)
            rname = '%s-%s'%(url, name)
            pattern = '%s/*subpath'%prefix

            ev.config.add_route(rname, pattern)
            ev.config.add_view(
                route_name =rname,
                view = StaticView(abspath, prefix))
        cfg['isurl'] = False
    else:
        cfg['isurl'] = True


class StaticView(object):

    def __init__(self, path, prefix):
        self.path = path
        self.prefix = '/%s'%prefix
        self.lprefix = len(self.prefix)+1

    def __call__(self, context, request):
        path_info = request.environ.get('PATH_INFO')
        if not path_info:
            return HTTPNotFound(request.url)

        # windows only
        path = os.path.join(
            self.path, os.path.join(*(path_info[self.lprefix:].split('/'))))

        if os.path.isfile(path):
            cfg = ptah.get_settings(ptah.CFG_ID_PTAH, request.registry)
            return _FileResponse(path, cfg['static_cache_max_age'])

        return HTTPNotFound(request.url)
