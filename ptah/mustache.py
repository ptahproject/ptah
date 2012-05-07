import os
import subprocess
from pyramid.view import view_config
from pyramid.path import AssetResolver
from pyramid.registry import Introspectable
from pyramid.httpexceptions import HTTPNotFound
from pyramid.exceptions import ConfigurationError

import ptah
from ptah.util import json

def check_output(*popenargs, **kwargs):
    """ python2.7 subprocess.checkoutput copy """
    process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
        raise subprocess.CalledProcessError(retcode, cmd, output=output)
    return output


ID_BUNDLE = 'ptah:mustache'
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

    discr = (ID_BUNDLE, name)

    resolver = AssetResolver()
    abs_path = resolver.resolve(path).abspath()

    if not path or not os.path.isdir(abs_path):
        raise ConfigurationError("Directory is required: %s"%path)

    intr = Introspectable(ID_BUNDLE, discr, name, ID_BUNDLE)
    intr['name'] = name
    intr['path'] = path
    intr['abs_path'] = abs_path
    intr['description'] = description

    storage = cfg.registry.setdefault(ID_BUNDLE, {})
    storage[name] = intr

    cfg.action(discr, introspectables=(intr,))


def compile_template(path, node_path):
    tmpl = ''
    cname = '%s.js'%path
    if os.path.exists(cname) and \
           (os.path.getmtime(path) < os.path.getmtime(cname)):
        with open(cname, 'rb') as f:
            tmpl = f.read()
    else:
        tmpl = check_output((node_path, HB, '-s', path))
        with open(cname, 'wb') as f:
            f.write(tmpl)

    return tmpl


template = """define("%s",["ptah","handlebars"],
function(ptah, Handlebars) {
var bundle={%s};ptah.Templates.bundles["%s"]=bundle;return bundle})
"""

def build_hb_bundle(name, intr, registry):
    cfg = ptah.get_settings(ptah.CFG_ID_PTAH, registry)

    node_path = cfg['nodejs-path']
    if not node_path:
        node_path = NODE_PATH

    if not node_path:
        raise RuntimeError("Can't find nodejs")

    path = intr['abs_path']

    templates = []

    for bname in os.listdir(path):
        bdir = os.path.join(path, bname)
        if not os.path.isdir(bdir):
            continue

        mustache = []
        for tname in os.listdir(bdir):
            if tname.endswith(ext_mustache) and tname[0] not in ('.#~'):
                fname = os.path.join(bdir, tname)
                tmpl = compile_template(fname, node_path)
                if tmpl:
                    mustache.append('"%s":Handlebars.template(%s)'%(
                        tname.rsplit('.', 1)[0], tmpl))

        templates.append(
            '"%s":new ptah.Templates("%s",{%s})'%(
                bname, bname, ','.join(mustache)))

    name = str(name)
    return template%(name, ',\n'.join(templates), name)


@view_config(route_name='ptah-mustache-bundle')
def bundle_view(request):
    name = request.matchdict['name']
    storage = request.registry.get(ID_BUNDLE)
    if not storage or name not in storage:
        return HTTPNotFound()

    name = str(name)
    response = request.response
    response.content_type = 'application/javascript'
    response.body = build_hb_bundle(name, storage[name], request.registry)
    return response


def list_bundles(request):
    res = []

    storage = request.registry.get(ID_BUNDLE)
    if not storage:
        return res

    for name in storage.keys():
        res.append((name, request.route_url('ptah-mustache-bundle', name=name)))

    return res
