import os
import tempfile
import subprocess
from pyramid.i18n import get_localizer
from pyramid.view import view_config
from pyramid.path import AssetResolver
from pyramid.compat import text_, bytes_, text_type
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
    if retcode: # pragma: nocover
        return ''
    return output


ID_BUNDLE = 'ptah:mustache'
ID_AMD_MODULE = 'ptah:amd-module'

try:
    if os.sys.platform == 'win32': # pragma: no cover
        NODE_PATH = r'C:\Program Files (x86)\nodejs\node.exe'
        os.stat(NODE_PATH)
    else:
        NODE_PATH = check_output(('which', 'node')).strip()
except: # pragma: no cover
    NODE_PATH = ''

HB = AssetResolver().resolve(
    'ptah:node_modules/handlebars/bin/handlebars').abspath()

ext_mustache = ('.mustache', '.hb')


def register_mustache_bundle(cfg, name, path='',description='',i18n_domain=''):
    """ Register mustache bundle;

    :param name: module name
    :param path: asset path
    :param description:
    :param i18n_domain: i18n domain

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
    intr['i18n_domain'] = i18n_domain

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
            tmpl = text_(f.read(), 'utf-8')

        if os.path.exists(iname):
            with open(iname, 'rb') as f:
                i18n.extend(json.loads(text_(f.read(),'utf-8')))
    else:
        text = []
        with open(tname, 'rb') as f:
            data = text_(f.read(), 'utf-8')

            # i18n
            pos = 0
            for start, end, message in extract_i18n_str(data):
                text.append(data[pos:start])
                text.append('{{#i18n-%s}}'%name)
                text.append(message)
                text.append('{{/i18n-%s}}'%name)
                pos = end
                i18n.append(message)

            text.append(data[pos:])

        with open(tname, 'wb') as f:
            f.write(bytes_(''.join(text), 'utf-8'))

        if i18n:
            with open(iname, 'wb') as f:
                f.write(bytes_(json.dumps(i18n), 'utf-8'))

        # compile
        tmpl = check_output((node_path, HB, '-s', tname))
        with open(cname, 'wb') as f:
            f.write(tmpl)

    return text_(tmpl, 'utf-8'), i18n


template = text_type("""define("%s",["ptah","handlebars"],
function(ptah, Handlebars) {
var bundle=%s;ptah.Templates.bundles["%s"]=bundle;%sreturn bundle})
""")

i18n_template = text_type("""\nHandlebars.registerHelper('%s',function(context, options) {return ptah.i18n(bundle, this, context, options)});
bundle.__i18n__ = %s;""")

class _r(object):
    def __init__(self, registry, locale):
        self.registry = registry
        self.locale_name = locale


def build_hb_bundle(name, intr, registry):
    cfg = ptah.get_settings(ptah.CFG_ID_PTAH, registry)

    node_path = cfg['nodejs-path']
    if not node_path:
        node_path = NODE_PATH

    if not cfg['mustache-cache']:
        cfg['mustache-cache'] = tempfile.mkdtemp()

    cache_dir = cfg['mustache-cache']

    if not node_path:
        raise RuntimeError("Can't find nodejs")

    path = intr['abs_path']
    i18n_domain = intr['i18n_domain']

    i18n = {}
    top = []
    templates = []

    for bname in os.listdir(path):
        bdir = os.path.join(path, bname)

        if not os.path.isdir(bdir):
            if bname.endswith(ext_mustache) and bname[0] not in ('.#~'):
                fname = os.path.join(path, bname)
                tmpl, _i18n = compile_template(name,fname,node_path,cache_dir)
                if tmpl:
                    top.append(text_type('"%s":Handlebars.template(%s)')%(
                        bname.rsplit('.', 1)[0], tmpl))
                if _i18n:
                    i18n.update(dict((v, None) for v in _i18n))
        else:
            mustache = []
            for tname in os.listdir(bdir):
                if tname.endswith(ext_mustache) and tname[0] not in ('.#~'):
                    fname = os.path.join(bdir, tname)
                    tmpl, _i18n = compile_template(
                        name, fname, node_path, cache_dir)
                    if tmpl:
                        mustache.append(
                            text_type('"%s":Handlebars.template(%s)')%(
                                tname.rsplit('.', 1)[0], tmpl))
                    if _i18n:
                        i18n.update(dict((v, None) for v in _i18n))

            templates.append(
                text_type('"%s":new ptah.Templates("%s",{%s})')%(
                    bname, bname, ','.join(mustache)))

    if top:
        tmpl = text_type('new ptah.Templates("%s",{%s},{%s})')%(
            name, text_type(',\n').join(top), text_type(',\n').join(templates))
    else:
        tmpl = text_type('{%s}')%(text_type(',\n').join(templates))

    name = str(name)

    if i18n:
        i18n_data = {}
        for lang in cfg['mustache-langs']:
            localizer = get_localizer(_r(registry, lang))
            for t, data in i18n.items():
                r = localizer.translate(t,i18n_domain)
                if t != r:
                    if t not in i18n_data:
                        i18n_data[t] = {}
                    i18n_data[t][lang] = r


        i18n_tmpl = i18n_template%('i18n-%s'%name, json.dumps(i18n_data))
        return template%(name, tmpl, name, i18n_tmpl)
    else:
        return template%(name, tmpl, name, '')


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


def extract_i18n_str(text):
    pos = 0
    first = last = -1

    messages = []

    while 1:
        first = text.find('{{#i18n}}', pos)
        if first >= 0:
            last = text.find('{{/i18n}}', first)
            if last >= 0:
                pos = last + 9
                messages.append((first, pos, text[first+9:last]))
                first = last = -1
                continue
        break

    return messages


def extract_i18n_mustache(fileobj, keywords, comment_tags, options):
    text = text_(fileobj.read(), 'utf-8')
    return [(first, None, message, [])
            for first, last, message in extract_i18n_str(text)]
