import os
import logging
from pyramid.path import AssetResolver
from pyramid.compat import escape, configparser, text_type, text_
from pyramid.view import view_config
from pyramid.registry import Introspectable
from pyramid.response import FileResponse
from pyramid.exceptions import ConfigurationError
from pyramid.httpexceptions import HTTPNotFound

import ptah
from ptah.util import json
from ptah.mustache import list_bundles

ID_AMD_SPEC = 'ptah:amd-spec'
ID_AMD_SPEC_ = 'ptah:amd-spec_'
ID_AMD_MODULE = 'ptah:amd-module'


def init_amd_spec(config, cache_max_age=None):
    cfg = ptah.get_settings(ptah.CFG_ID_PTAH, config.registry)
    config.registry[ID_AMD_SPEC] = {}
    if not cfg['amd-spec']:
        return

    if not cfg['amd-dir']:
        raise ConfigurationError("amd-dir is required.")

    resolver = AssetResolver()
    directory = resolver.resolve(cfg['amd-dir']).abspath()

    specs = {}
    for item in cfg['amd-spec']:
        if ':' not in item:
            spec = ''
            specfile = item
        else:
            spec, specfile = item.split(':',1)

        if spec in specs:
            raise ConfigurationError("Spec '%s' already defined."%spec)

        specs[spec] = specfile

    spec_mods = {}

    for spec, specfile in specs.items():
        f = resolver.resolve(specfile).abspath()

        parser = configparser.SafeConfigParser()
        parser.read(f)

        mods = {}
        for section in parser.sections():
            if section.endswith('.js'):
                items = dict(parser.items(section))
                url = items.get('url', '')
                modules = items.get('modules', '')
                modules = [s for s in [s.strip() for s in modules.split()]
                           if not s.startswith('#')]

                if url:
                    item = {'url': url, 'name': section}
                elif modules:
                    item = {'name': section,
                            'path': os.path.join(directory,section)}

                mods[section] = item
                for mod in modules:
                    mods[mod] = item

        spec_mods[spec] = mods

    config.registry[ID_AMD_SPEC] = spec_mods
    config.registry[ID_AMD_SPEC_] = cache_max_age


def register_amd_module(cfg, name, path, description='', require=()):
    """ register amd js module

    :param name: name
    :param path: asset path
    :param description: module description
    :param deps: module dependencies
    """
    discr = (ID_AMD_MODULE, name)

    intr = Introspectable(ID_AMD_MODULE, discr, name, ID_AMD_MODULE)
    intr['name'] = name
    intr['path'] = path
    intr['description'] = description

    if isinstance(require, str):
        require = (require,)
    intr['require'] = require

    storage = cfg.registry.setdefault(ID_AMD_MODULE, {})
    storage[name] = intr

    cfg.action(discr, introspectables=(intr,))


def extract_mod(filename, path, log):
    mods = {}
    name = filename.split('.js')[0]
    if os.path.isfile(path):
        text = text_(open(path, 'rb').read())
        pos = 0
        while 1:
            p1 = text.find('define(', pos)
            if p1 < 0:
                break

            p2 = text.find('function(', p1)
            if p2 < 0:
                break

            pos = p2
            chunk = ''.join(ch.strip() for ch in text[p1+7:p2].split())
            if chunk.startswith("'") or chunk.startswith('"'):
                name, chunk = chunk.split(',',1)
                name = ''.join(ch for ch in name if ch not in "\"'[]")
            else:
                log.warning("Empty name is not supported, %s"%filename)
                continue

            deps = [d for d in
                    ''.join(ch for ch in chunk
                            if ch not in "\"'[]").split(',') if d]
            mods[name] = deps

    return mods.items()


def register_amd_dir(cfg, path):
    """ read and load amd modules from directory

    :param path: asset path
    """
    log = logging.getLogger('ptah.amd')

    resolver = AssetResolver()
    directory = resolver.resolve(path).abspath()

    mods = []
    for filename in os.listdir(directory):
        if not filename.endswith('.js'):
            continue
        for name, deps in extract_mod(filename,
                                      os.path.join(directory, filename), log):
            p = os.path.join(path, filename)
            mods.append((name, p))

    for name, p in sorted(mods):
        register_amd_module(cfg, name, p)
        log.info("Add amd module: %s path:%s"%(name, p))


amd_init_tmpl = """
var ptah_amd_modules = {\n%(mods)s}
%(exrta)s

curl({dontAddFileExt:'.', paths: ptah_amd_modules})
"""

@view_config(route_name='ptah-amd-spec')
def amd_spec(request):
    name = request.matchdict['name']
    specname = request.matchdict['specname']

    spec = request.registry.get(ID_AMD_SPEC, {}).get(specname, ())
    if name not in spec or 'path' not in spec[name]:
        return HTTPNotFound()

    return FileResponse(
        spec[name]['path'], request, request.registry.get(ID_AMD_SPEC_))


@view_config(route_name='ptah-amd-init')
def amd_init(request):
    specname = request.matchdict['specname']
    storage = request.registry.get(ID_AMD_MODULE)
    spec = request.registry.get(ID_AMD_SPEC, {}).get(specname)
    if spec is None and specname != '_':
        return HTTPNotFound()

    js = []

    if spec is None:
        spec = {}

    if storage:
        for name, intr in storage.items():
            path = intr['path']
            info = spec.get(name)
            if info and 'path' in info:
                url = request.route_url(
                    'ptah-amd-spec', specname=specname, name=info['name'])
            else:
                url = '%s'%request.static_url(path)

            if url.endswith('.css'):
                js.append('"%s.css": "%s"'%(name, url))
            else:
                js.append('"%s": "%s"'%(name, url))                

    for name, url in list_bundles(request):
        info = spec.get(name)
        if info and 'path' in info:
            url = request.route_url(
                'ptah-amd-spec', specname=specname, name=info['name'])

        js.append('"%s":"%s"'%(name, url))

    options = {'ptah_host': request.application_url,
               'ptah_dt': {'short': 'm/d/yy h:MM TT',
                           'medium': 'mmm d, yyyy h:MM:ss TT',
                           'full': 'mmmm, d, yyyy h:MM:ss TT Z'}
               }

    response = request.response
    response.content_type = 'application/javascript'
    response.text = text_type(amd_init_tmpl%{
        'app_url': request.application_url,
        'mods': ',\n'.join(sorted(js)),
        'exrta': '\n'.join('var %s = %s'%(name, json.dumps(val))
                           for name, val in options.items())})
    return response


def render_amd_includes(request, spec='', bundles=(), init=True):
    registry = request.registry
    cfg = ptah.get_settings(ptah.CFG_ID_PTAH, request.registry)

    c_tmpls = []
    if spec and cfg['amd-enabled']:
        specstorage = request.registry.get(ID_AMD_SPEC, {})
        specdata = specstorage.get(spec)
        if specdata is None:
            raise RuntimeError("Spec '%s' is not found."%spec)
    else:
        spec = '_'
        specdata = ()

    c_tmpls.append(
        '<script src="%s"> </script>'%
        request.static_url('ptah:static/lib/curl.js'))
    c_tmpls.append(
        '<script src="%s/_amd_%s.js"> </script>'%(
            request.application_url, spec))

    for name in (bundles if not isinstance(bundles, str) else (bundles,)):
        name = '%s.js'%name
        if name in specdata:
            c_tmpls.append(
                '<script src="%s"></script>'%
                request.route_url('ptah-amd-spec',specname=spec,name=name))

    if init:
        c_tmpls.append(
            "<script>curl(['domReady!']).next(['ptah'], function(ptah) {ptah.init(ptah_amd_modules)})</script>")

    return '\n'.join(c_tmpls)


def render_css_includes(request, css=()):
    if isinstance(css, basestring):
        css = (css,)

    return ("<script>curl([%s],{paths:ptah_amd_modules})</script>" %
            ','.join("'css!%s.css'"%c for c in css))


def render_amd_container(request, name, **kw):
    registry = request.registry
    attrs = ['ptah="%s"'%name, ' '.join('data-%s="%s"'%(key, escape(val))
                                        for key, val in kw.items())]
    return '<div %s></div>'%(' '.join(v for v in attrs if v))
