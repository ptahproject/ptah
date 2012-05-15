import re
import os
import tempfile
import subprocess
from pyramid.view import view_config
from pyramid.path import AssetResolver
from pyramid.compat import text_
from pyramid.registry import Introspectable
from pyramid.httpexceptions import HTTPNotFound
from pyramid.exceptions import ConfigurationError

import ptah
from ptah.util import json

i18n_re = re.compile('{{#i18n}}(.*){{/i18n}}')


def check_output(*popenargs, **kwargs):
    """ python2.7 subprocess.checkoutput copy """
    process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode: # pragma: nocover
        return ''
    return output


ID_BUNDLE = 'ptah:mustache'
ID_AMD_MODULE = 'ptah:amd-module'
NODE_PATH = check_output(('which', 'node')).strip()
HB = AssetResolver().resolve(
    'ptah:node_modules/handlebars/bin/handlebars').abspath()

ext_mustache = ('.mustache', '.handlebars')


def register_mustache_bundle(cfg, name, path='', description=''):
    """ Register mustache bundle;

    :param name: module name
    :param path: asset path
    :param description:

    """
    resolver = AssetResolver()
    d = resolver.resolve(path).abspath()

    if not os.path.isdir(d):
        raise ConfigurationError("Directory is required: %s"%path)

    discr = (ID_AMD_MODULE, name)

    resolver = AssetResolver()
    abs_path = resolver.resolve(path).abspath()

    if not path or not os.path.isdir(abs_path):
        raise ConfigurationError("Directory is required: %s"%path)

    intr = Introspectable(ID_AMD_MODULE, discr, name, ID_AMD_MODULE)
    intr['name'] = name
    intr['path'] = path
    intr['abs_path'] = abs_path
    intr['description'] = description

    storage = cfg.registry.setdefault(ID_BUNDLE, {})
    storage[name] = intr

    cfg.action(discr, introspectables=(intr,))


def compile_template(name, path, node_path, cache_dir):
    tmpl = ''

    dir, tname = os.path.split(path)
    tname = os.path.join(
        cache_dir, '%s-%s-%s'%(name, os.path.split(dir)[-1], tname))

    # copy to temp dir
    if not os.path.exists(tname) or \
           (os.path.getmtime(path) > os.path.getmtime(tname)):
        with open(tname, 'wb') as f:
            f.write(open(path, 'rb').read())

    i18n = []

    # check if .js file exists
    cname = '%s.js'%tname
    iname = '%s.i18n'%tname
    if os.path.exists(cname) and \
           (os.path.getmtime(tname) < os.path.getmtime(cname)):
        with open(cname, 'rb') as f:
            tmpl = f.read()

        if os.path.exists(iname):
            with open(iname, 'rb') as f:
                i18n.extend([v for v in f.read().split('\n') if v])
    else:
        text = []
        with open(tname, 'rb') as f:
            data = f.read()

            pos = 0
            for m in i18n_re.finditer(data):
                start, end = m.span()
                s = data[start+9:end-9]
                text.append(data[pos:start])
                text.append('{{#i18n-%s}}'%name)
                text.append(s)
                text.append('{{/i18n-%s}}'%name)
                pos = end
                i18n.append(s)

            text.append(data[pos:])

        with open(tname, 'wb') as f:
            f.write(''.join(text))

        if i18n:
            with open(iname, 'wb') as f:
                f.write('\n'.join(i18n))

        # compile
        tmpl = check_output((node_path, HB, '-s', tname))
        with open(cname, 'wb') as f:
            f.write(tmpl)

    return tmpl, i18n


template = """define("%s",["ptah","handlebars"],
function(ptah, Handlebars) {
var bundle={%s};ptah.Templates.bundles["%s"]=bundle;%sreturn bundle})
"""

i18n_template = """\nHandlebars.registerHelper('%s',function(context, options) {return ptah.i18n(bundle, this, context, options)});"""

def build_hb_bundle(name, intr, registry):
    cfg = ptah.get_settings(ptah.CFG_ID_PTAH, registry)

    node_path = cfg['nodejs-path']
    if not node_path:
        node_path = NODE_PATH

    if not cfg['amd-cache']:
        cfg['amd-cache'] = tempfile.mkdtemp()

    cache_dir = cfg['amd-cache']

    if not node_path:
        raise RuntimeError("Can't find nodejs")

    path = intr['abs_path']

    i18n = {}
    templates = []

    for bname in os.listdir(path):
        bdir = os.path.join(path, bname)
        if not os.path.isdir(bdir):
            continue

        mustache = []
        for tname in os.listdir(bdir):
            if tname.endswith(ext_mustache) and tname[0] not in ('.#~'):
                fname = os.path.join(bdir, tname)
                tmpl, _i18n = compile_template(name,fname,node_path,cache_dir)
                if tmpl:
                    mustache.append('"%s":Handlebars.template(%s)'%(
                        tname.rsplit('.', 1)[0], tmpl))
                if _i18n:
                    i18n.update(dict((v, '') for v in _i18n))

        templates.append(
            '"%s":new ptah.Templates("%s",{%s})'%(
                bname, bname, ','.join(mustache)))

    i18n_tmpl = i18n_template%('i18n-%s'%name) if i18n else ''

    name = str(name)
    return template%(name, ',\n'.join(templates), name, i18n_tmpl)


@view_config(route_name='ptah-mustache-bundle')
def bundle_view(request):
    name = request.matchdict['name']
    storage = request.registry.get(ID_BUNDLE)
    if not storage or name not in storage:
        return HTTPNotFound()

    name = str(name)
    response = request.response
    response.content_type = 'application/javascript'
    response.text = text_(
        build_hb_bundle(name, storage[name], request.registry), 'utf-8')
    return response


def list_bundles(request):
    res = []

    storage = request.registry.get(ID_BUNDLE)
    if not storage:
        return res

    for name in storage.keys():
        res.append((name, request.route_url('ptah-mustache-bundle', name=name)))

    return res
