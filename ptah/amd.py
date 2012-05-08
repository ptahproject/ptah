import os
from pyramid.path import AssetResolver
from pyramid.compat import escape, configparser, text_type
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
    if not cfg['amd-specs']:
        return

    if not cfg['amd-spec-dir']:
        raise ConfigurationError("amd-spec-dir is required.")

    resolver = AssetResolver()
    directory = resolver.resolve(cfg['amd-spec-dir']).abspath()

    specs = {}
    for item in cfg['amd-specs']:
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
                    mods[section] = {'url':url}
                elif modules:
                    mods[section] = {'path': os.path.join(directory, section)}

                #for mod in modules:
                #    mods[mod] = item

        spec_mods[spec] = mods

    config.registry[ID_AMD_SPEC] = spec_mods
    config.registry[ID_AMD_SPEC_] = cache_max_age


def register_amd_module(cfg, name, path, description=''):
    """ register amd js module

    :param name: name
    :param path: asset path
    :param description:
    """
    discr = (ID_AMD_MODULE, name)

    intr = Introspectable(ID_AMD_MODULE, discr, name, ID_AMD_MODULE)
    intr['name'] = name
    intr['path'] = path
    intr['description'] = description

    storage = cfg.registry.setdefault(ID_AMD_MODULE, {})
    storage[name] = path

    cfg.action(discr, introspectables=(intr,))


amd_init_tmpl = """
var ptah_amd_modules = {\n%(mods)s}

%(exrta)s

curl({paths: ptah_amd_modules || {}})
curl(
  {paths: ptah_amd_modules || {}}, ['jquery'],
  function($) {
    $(function() {
      curl(['ptah','ptah-date-format']).then(function(ptah) {
          ptah.scan_and_create()
          window.ptah = ptah
          window.ptah_jquery = $
        })
    })
  }
)
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
        for name, path in storage.items():
            info = spec.get(name)
            if info and 'path' in info:
                url = request.route_url(
                    'ptah-amd-spec', specname=specname, name=info['name'])
            else:
                url = '%s'%request.static_url(path)

            js.append('"%s": "%s"'%(name, url[:-3]))

    for name, url in list_bundles(request):
        info = spec.get(name)
        if info and 'path' in info:
            url = request.route_url(
                'ptah-amd-spec', specname=specname, name=info['name'])

        js.append('"%s":"%s"'%(name, url[:-3]))

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


amd_incl = """
<script src="%(app_url)s/_amd_%(specname)s.js"> </script>
%(components)s
"""

def render_amd_includes(request, spec='', bundles=()):
    registry = request.registry
    cfg = ptah.get_settings(ptah.CFG_ID_PTAH, request.registry)

    ptah.include(request, 'curl')

    c_tmpls = []
    if cfg['amd-spec-enabled']:
        specstorage = request.registry.get(ID_AMD_SPEC, {})
        specdata = specstorage.get(spec)
        if specdata is None:
            raise RuntimeError("Spec '%s' is not found."%spec)
    else:
        spec = '_'
        specdata = ()

    for name in (bundles if not isinstance(bundles, str) else (bundles,)):
        name = '%s.js'%name
        if name in specdata:
            c_tmpls.append(
                '<script src="%s"></script>'%
                request.route_url('ptah-amd-spec',specname=spec,name=name))

    return amd_incl%{'app_url': request.application_url,
                     'specname': spec,
                     'components': '\n'.join(c_tmpls)}


def render_amd_container(request, name, **kw):
    registry = request.registry
    opt =' '.join('data-%s="%s"'%(key, escape(val))
                  for key, val in kw.items())
    return '<div ptah="%s" class="ptah-container" %s></div>'%(name, opt)
