import os
import hashlib
import logging
from pyramid.path import AssetResolver
from pyramid.compat import configparser, text_type, string_types, text_
from pyramid.view import view_config
from pyramid.registry import Introspectable
from pyramid.response import FileResponse
from pyramid.exceptions import ConfigurationError
from pyramid.httpexceptions import HTTPNotFound

from .handlebars import list_bundles

log = logging.getLogger('ptah.amdjs')

ID_AMD_SPEC = 'ptah.amdjs:amd-spec'
ID_AMD_SPEC_ = 'pyramid_amdsj:amd-spec_'
ID_AMD_MODULE = 'ptah.amdjs:amd-module'
ID_AMD_BUILD = 'ptah.amdjs:build-init'
ID_AMD_MD5 = 'ptah.amdjs:md5-init'
ID_AMD_BUILD_MD5 = 'ptah.amdjs:build-md5-init'

JS_MOD = 1
CSS_MOD = 2

RESOLVER = AssetResolver()
CURL_PATH = RESOLVER.resolve('ptah.amdjs:static/lib/curl.js').abspath()


def init_amd_spec(config, cache_max_age=None):
    cfg = config.get_settings()
    if not cfg['amd.spec']:
        return

    if not cfg['amd.spec-dir']:
        raise ConfigurationError("amd.spec-dir is required.")

    directory = RESOLVER.resolve(cfg['amd.spec-dir']).abspath()

    # register static view
    config.add_static_view('_amdjs/bundles/', directory)

    specs = {}
    for spec, specfile in cfg['amd.spec']:
        if spec in specs:
            raise ConfigurationError("Spec '%s' already defined." % spec)

        specs[spec] = specfile

    spec_mods = {}

    for spec, specfile in specs.items():
        f = RESOLVER.resolve(specfile).abspath()

        parser = configparser.SafeConfigParser()
        parser.read(f)

        mods = {}
        for section in parser.sections():
            items = dict(parser.items(section))

            if section.endswith('.js'):
                modules = [
                    s for s in
                    [s.strip() for s in items.get('modules', '').split()]
                    if not s.startswith('#')]
                if modules:
                    md5 = hashlib.md5()
                    fpath = os.path.join(directory, section)
                    with open(fpath, 'rb') as f:
                        md5.update(f.read())

                    item = {'name': section,
                            'md5': md5.hexdigest(),
                            'path': fpath}

                mods[section] = item
                for mod in modules:
                    mods[mod] = item

        spec_mods[spec] = mods
        spec_mods['%s-init' % spec] = os.path.join(
            directory, 'init-%s.js' % spec)

    config.registry[ID_AMD_SPEC] = spec_mods
    config.registry[ID_AMD_SPEC_] = cache_max_age


def add_js_module(cfg, name, path, description='', requires=()):
    """ register amd js module

    :param name: name
    :param path: asset path
    :param description: module description
    :param requires: module dependencies
    """
    discr = (ID_AMD_MODULE, name)

    intr = Introspectable(ID_AMD_MODULE, discr, name, ID_AMD_MODULE)
    intr['name'] = name
    intr['path'] = path
    intr['description'] = description
    intr['tp'] = JS_MOD

    filepath = RESOLVER.resolve(path).abspath()
    md5 = hashlib.md5()
    with open(filepath, 'rb') as f:
        md5.update(f.read())

    intr['md5'] = md5.hexdigest()

    if isinstance(requires, str):
        requires = (requires,)
    intr['requires'] = requires

    storage = cfg.registry.setdefault(ID_AMD_MODULE, {})
    storage[name] = intr

    cfg.action(discr, introspectables=(intr,))
    log.info("Add js module: %s path:%s" % (name, path))


def add_css_module(cfg, name, path, description=''):
    """ register css module

    :param name: name
    :param path: asset path
    :param description: module description
    """
    discr = (ID_AMD_MODULE, name)

    intr = Introspectable(ID_AMD_MODULE, discr, name, ID_AMD_MODULE)
    intr['name'] = name
    intr['path'] = path
    intr['description'] = description
    intr['tp'] = CSS_MOD

    filepath = RESOLVER.resolve(path).abspath()
    md5 = hashlib.md5()
    with open(filepath, 'rb') as f:
        md5.update(f.read())
    intr['md5'] = md5.hexdigest()

    storage = cfg.registry.setdefault(ID_AMD_MODULE, {})
    storage[name] = intr

    cfg.action(discr, introspectables=(intr,))
    log.info("Add css module: %s path:%s" % (name, path))


def extract_mod(name, text, path):
    mods = {}

    pos = 0
    while 1:
        p1 = text.find('define(', pos)
        if p1 < 0:
            break

        p2 = text.find('function(', p1)
        if p2 < 0:
            break

        pos = p2
        chunk = ''.join(ch.strip() for ch in text[p1 + 7:p2].split())
        if chunk.startswith("'") or chunk.startswith('"'):
            name, chunk = chunk.split(',', 1)
            name = ''.join(ch for ch in name if ch not in "\"'[]")
        else:
            log.warning("Empty name is not supported, %s.js" % name)
            continue

        deps = [d for d in
                ''.join(ch for ch in chunk
                        if ch not in "\"'[]").split(',') if d]
        mods[name] = deps

    if not mods:
        log.warning("Can't detect amdjs module name for: %s" % path)
        raise ConfigurationError(
            "Can't detect amdjs module name for: %s" % path)

    return mods.items()


def add_amd_dir(cfg, path):
    """ read and load amd modules from directory

    :param path: asset path
    """
    directory = RESOLVER.resolve(path).abspath()

    mods = []
    for filename in os.listdir(directory):
        p = os.path.join(path, filename)

        if filename.endswith('.js'):
            with open(os.path.join(directory, filename), 'rb') as f:
                for name, deps in extract_mod(
                        filename[:-3], text_(f.read()), p):
                    mods.append((name, p, JS_MOD))
        if filename.endswith('.css'):
            mods.append((filename, p, CSS_MOD))

    for name, p, mod in sorted(mods):
        if mod == JS_MOD:
            add_js_module(cfg, name, p)
            log.info("Add js module: %s path:%s" % (name, p))
        elif mod == CSS_MOD:
            add_css_module(cfg, name, p)
            log.info("Add css module: %s path:%s" % (name, p))

    return directory


AMD_INIT_TMPL = """
%(curl)s

var pyramid_amd_modules = {\n%(mods)s}

curl({dontAddFileExt:'.', paths: pyramid_amd_modules})
"""


def build_md5(request, specname):
    data = request.registry[ID_AMD_MD5]

    h = data.get(specname)
    if h is None:
        cfg = request.registry.settings
        specstorage = request.registry[ID_AMD_SPEC]
        specdata = specstorage.get(specname)

        initfile = '%s-init' % specname
        if specdata and cfg['amd.enabled'] and initfile in specstorage:
            with open(specstorage[initfile], 'r') as f:
                line = f.readline()
                h = line.split('||', 2)[1]
        else:
            initf = build_init(request, specname)

            md5 = hashlib.md5()
            md5.update(initf.encode('utf-8'))

            h = request.registry[ID_AMD_MD5][specname] = md5.hexdigest()

    return h


def build_init(request, specname, extra=()):
    storage = request.registry.get(ID_AMD_MODULE)

    spec_data = request.registry[ID_AMD_SPEC].get(specname)
    if spec_data is None and specname != '_':
        return None

    js = list(extra)
    if spec_data is None:
        spec_data = {}

    app_url = request.application_url
    app_url_len = len(app_url)

    spec_cache = {}

    if storage:
        for name, intr in storage.items():
            path = intr['path']
            info = spec_data.get(name)
            if info:
                url = request.static_url(
                    info['path'], _query={'_v': info['md5']})
            else:
                url = '%s' % request.static_url(path)
                if 'md5' in intr:
                    url = '%s?_v=%s' % (url, intr['md5'])

            if url.startswith(app_url):
                url = url[app_url_len:]

            js.append('"%s": "%s"' % (name, url))

    # list handlebars bundles, in case if bundle is part of spec
    for name, url in list_bundles(request):
        info = spec_data.get(name)
        if info:
            url = request.static_url(info['path'], _query={'_v': info['md5']})

        if url.startswith(app_url):
            url = url[app_url_len:]

        js.append('"%s":"%s"' % (name, url))

    with open(CURL_PATH, 'r') as f:
        return text_type(AMD_INIT_TMPL % {
            'curl': f.read(), 'mods': ',\n'.join(sorted(js))})


@view_config(route_name='pyramid-amd-init')
def amd_init(request, **kw):
    cfg = request.registry.settings
    specstorage = request.registry[ID_AMD_SPEC]
    specname = request.matchdict['specname']
    specdata = specstorage.get(specname)
    cache_max_age = 31536000 if request.params.get('_v') else None

    initfile = '%s-init' % specname
    if specdata and cfg['amd.enabled'] and initfile in specstorage:
        return FileResponse(specstorage[initfile], request, cache_max_age)

    text = request.registry[ID_AMD_BUILD](request, specname)
    if text is None:
        return HTTPNotFound()

    response = request.response
    response.content_type = 'application/javascript'
    response.text = text

    if cache_max_age:
        response.cache_expires = cache_max_age

    return response


def request_amd_init(request, spec='', bundles=()):
    reg = request.registry
    cfg = request.registry.settings

    c_tmpls = []
    if spec and cfg['amd.enabled']:
        specstorage = reg[ID_AMD_SPEC]
        specdata = specstorage.get(spec)
        if specdata is None:
            raise RuntimeError("Spec '%s' is not found." % spec)
    else:
        spec = '_'
        specdata = ()

    if spec != '_':
        initfile = '%s-init' % spec
        c_tmpls.append(
            '<script src="%s"> </script>' % (
                request.static_url(
                    specstorage[initfile],
                    _query={'_v': reg[ID_AMD_BUILD_MD5](request, spec)})))
    else:
        c_tmpls.append(
            '<script src="%s"> </script>' % (
                request.route_url(
                    'pyramid-amd-init', specname=spec,
                    _query={'_v': reg[ID_AMD_BUILD_MD5](request, spec)})))

    for name in (bundles if not isinstance(bundles, str) else (bundles,)):
        name = '%s.js' % name
        if name in specdata:
            c_tmpls.append(
                '<script src="%s"></script>' %
                request.static_url(specdata[name]['path']))

    return '\n'.join(c_tmpls)


def request_includes(request, js=(), css=()):
    if isinstance(js, string_types):
        js = (js,)

    mods = ["'%s'" % c for c in js]

    if isinstance(css, string_types):
        css = (css,)

    mods.extend("'css!%s.css'" % c for c in css)

    return ('<script type="text/javascript">'
            'curl({paths:pyramid_amd_modules},[%s])</script>' %
            ','.join(mods))


def request_css_includes(request, css=()):
    if isinstance(css, string_types):
        css = (css,)

    return ('<script type="text/javascript">'
            'curl({paths:pyramid_amd_modules},[%s])</script>' %
            ','.join("'css!%s'" % c for c in css))
