import os
import shutil
import hashlib
import logging
import tempfile
from pyramid.i18n import get_localizer
from pyramid.view import view_config
from pyramid.path import AssetResolver
from pyramid.compat import text_, bytes_, text_type
from pyramid.registry import Introspectable
from pyramid.httpexceptions import HTTPNotFound
from pyramid.exceptions import ConfigurationError

from ptah.amdjs import compat
from ptah.amdjs.compat import json, check_output

log = logging.getLogger('ptah.amdjs')

VER = b'1.0.0-rc.3'
VERSION = VER.decode()
ID_BUNDLE = 'ptah.amdjs:handlebars'
ID_AMD_MODULE = 'ptah.amdjs:amd-module'

HB = AssetResolver().resolve(
    'ptah.amdjs:node_modules/handlebars/bin/handlebars').abspath()

ext_handlebars = ('.mustache', '.hb')


def register_handlebars_bundle(
        cfg, name, path='', description='', i18n_domain=''):
    """ Register handlebars bundle;

    :param name: module name
    :param path: asset path
    :param description:
    :param i18n_domain: i18n domain

    """
    resolver = AssetResolver()
    abs_path = resolver.resolve(path).abspath()

    if not path or not os.path.isdir(abs_path):
        raise ConfigurationError("Directory is required: %s" % path)

    discr = (ID_AMD_MODULE, name)

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
        cache_dir, '%s-%s-%s' % (name, os.path.split(dir)[-1], tname))

    # copy to temp dir
    if ((not os.path.exists(tname) or
         (os.path.getmtime(path) > os.path.getmtime(tname)))):

        shutil.copyfile(path, tname)

    i18n = []

    # check if .js file exists
    if node_path:
        cname = '%s.js.%s' % (tname, VERSION)
    else:
        cname = '%s.pre' % tname

    iname = '%s.i18n' % tname
    if (os.path.exists(cname) and
            (os.path.getmtime(tname) <= os.path.getmtime(cname))):
        with open(cname, 'rb') as f:
            tmpl = text_(f.read())

        if os.path.exists(iname):
            with open(iname, 'rb') as f:
                i18n.extend(json.loads(text_(f.read())))
    else:
        text = []
        with open(tname, 'rb') as f:
            data = text_(f.read())

            # i18n
            pos = 0
            for start, end, message in extract_i18n_str(data):
                text.append(data[pos:start])
                text.append('{{#i18n-%s}}' % name)
                text.append(message)
                text.append('{{/i18n-%s}}' % name)
                pos = end
                i18n.append(message)

            text.append(data[pos:])

        tmpl = bytes_(''.join(text), 'utf-8')
        with open(tname, 'wb') as f:
            f.write(tmpl)

        if i18n:
            with open(iname, 'wb') as f:
                f.write(bytes_(json.dumps(i18n), 'utf-8'))

        # compile
        if node_path:
            tmpl = check_output((node_path, HB, '-s', tname))
            if tmpl is None:
                tmpl = b''
                log.error('Compilation is failed: %s' % path)

        with open(cname, 'wb') as f:
            f.write(tmpl)

    return text_(tmpl, 'utf-8'), i18n


template = text_type("""define("%s",["pyramid:templates","handlebars"],
function(templates, Handlebars) {
var bundle=%s;templates.bundles["%s"]=bundle;%sreturn bundle})
""")

i18n_template = text_type(
    "\nHandlebars.registerHelper('%s',function(context, options) "
    "{return templates.i18n(bundle, this, context, options)});\n"
    "bundle.__i18n__ = %s;")


class _r(object):
    def __init__(self, registry, locale):
        self.registry = registry
        self.locale_name = locale


def build_hb_bundle(name, intr, registry):
    cfg = registry.settings

    node_path = cfg['amd.node']
    if not node_path:
        node_path = compat.NODE_PATH

    if not cfg['amd.tmpl-cache']:
        cfg['amd.tmpl-cache'] = tempfile.mkdtemp()

    cache_dir = cfg['amd.tmpl-cache']

    path = intr['abs_path']
    i18n_domain = intr['i18n_domain']

    i18n = {}
    top = []
    templates = []

    for bname in os.listdir(path):
        bdir = os.path.join(path, bname)

        if not os.path.isdir(bdir):
            if bname.endswith(ext_handlebars) and bname[0] not in ('.#~'):
                fname = os.path.join(path, bname)
                tmpl, _i18n = compile_template(
                    name, fname, node_path, cache_dir)

                if tmpl:
                    top.append((bname.rsplit('.', 1)[0], tmpl))

                if _i18n:
                    i18n.update(dict((v, None) for v in _i18n))
        else:
            hb_tmpls = []
            for tname in os.listdir(bdir):
                if tname.endswith(ext_handlebars) and tname[0] not in ('.#~'):
                    fname = os.path.join(bdir, tname)
                    tmpl, _i18n = compile_template(
                        name, fname, node_path, cache_dir)
                    if tmpl:
                        hb_tmpls.append((tname.rsplit('.', 1)[0], tmpl))
                    if _i18n:
                        i18n.update(dict((v, None) for v in _i18n))

            if node_path:
                hb_tmpls = (
                    text_type('"%s":Handlebars.template(%s)') % (
                        name, tmpl) for name, tmpl in hb_tmpls)
            else:
                hb_tmpls = (
                    text_type('"%s":Handlebars.compile(%s)') % (
                        name, json.dumps(tmpl)) for name, tmpl in hb_tmpls)

            templates.append(
                text_type('"%s":new templates.Bundle("%s",{%s})') % (
                    bname, bname, ','.join(hb_tmpls)))

    if top:
        if node_path:
            top = (text_type('"%s":Handlebars.template(%s)') % (
                name, tmpl) for name, tmpl in top)
        else:
            top = (text_type('"%s":Handlebars.compile(%s)') % (
                name, json.dumps(tmpl)) for name, tmpl in top)

        tmpl = text_type('new templates.Bundle("%s",{%s},{%s})') % (
            name, text_type(',\n').join(top), text_type(',\n').join(templates))
    else:
        tmpl = text_type('{%s}') % (text_type(',\n').join(templates))

    name = str(name)

    if i18n:
        i18n_data = {}
        for lang in cfg['amd.tmpl-langs']:
            localizer = get_localizer(_r(registry, lang))
            for t, data in i18n.items():
                r = localizer.translate(t, i18n_domain)
                if t != r:
                    if t not in i18n_data:
                        i18n_data[t] = {}
                    i18n_data[t][lang] = r

        i18n_tmpl = i18n_template % ('i18n-%s' % name, json.dumps(i18n_data))
        res = template % (name, tmpl, name, i18n_tmpl)
    else:
        res = template % (name, tmpl, name, '')

    res = text_(res, 'utf-8')

    md5 = hashlib.md5()
    md5.update(res.encode('latin-1'))

    intr['md5'] = md5.hexdigest()

    return res


@view_config(route_name='pyramid-hb-bundle')
def bundle_view(request):
    name = request.matchdict['name']
    storage = request.registry.get(ID_BUNDLE)
    if not storage or name not in storage:
        return HTTPNotFound()

    name = str(name)
    response = request.response
    response.content_type = 'application/javascript'
    response.text = build_hb_bundle(name, storage[name], request.registry)
    return response


def list_bundles(request):
    res = []

    storage = request.registry.get(ID_BUNDLE)
    if not storage:
        return res

    for name, intr in storage.items():
        build_hb_bundle(name, intr, request.registry)

        url = request.route_url(
            'pyramid-hb-bundle', name=name, _query={'_v': intr['md5']})
        res.append((name, url))

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
                messages.append((first, pos, text[first + 9:last]))
                first = last = -1
                continue
        break

    return messages


def extract_i18n(fileobj, keywords, comment_tags, options):
    text = text_(fileobj.read(), 'utf-8')
    return [(first, None, message, [])
            for first, last, message in extract_i18n_str(text)]
