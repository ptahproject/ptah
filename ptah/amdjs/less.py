"""less bundles."""

import hashlib
import os
import logging
import tempfile
from pyramid.exceptions import ConfigurationError
from pyramid.httpexceptions import HTTPNotFound, HTTPInternalServerError
from pyramid.registry import Introspectable
from pyramid.view import view_config
from pyramid.path import AssetResolver

from .compat import check_output

log = logging.getLogger('ptah.amdjs')

ID_BUNDLE = 'ptah.amdjs:less'

RECESS = AssetResolver().resolve(
    'ptah.amdjs:node_modules/recess/bin/recess').abspath()


def register_less_bundle(cfg, name, path, description='', watchdir=None):
    """ Register less bundle;

    :param name: module name
    :param path: asset path
    :param description:
    """
    resolver = AssetResolver()
    abs_path = resolver.resolve(path).abspath()

    if not os.path.isfile(abs_path):
        raise ConfigurationError("less file is required: %s" % path)

    discr = (ID_BUNDLE, name)

    intr = Introspectable(ID_BUNDLE, discr, name, ID_BUNDLE)
    intr['name'] = name
    intr['path'] = path
    intr['abs_path'] = abs_path
    intr['watchdir'] = watchdir or os.path.dirname(abs_path)
    intr['description'] = description

    storage = cfg.registry.setdefault(ID_BUNDLE, {})
    storage[name] = intr

    cfg.action(discr, introspectables=(intr,))


def compile_less(name, path, node_path, cache_dir, compress=False):
    args = [node_path, RECESS, path, '--compile']
    if compress:
        args.append('--compress')

    tmpl = check_output(args)
    if not tmpl:
        tmpl = b''
        errs = check_output(args + ['false']) or b''
        log.error('Compilation is failed: %s%s' % (path, errs.decode()))
        raise ValueError('Compilation is failed: %s' % path)

    return tmpl


def files_changed(mtime, basedir):
    for name in os.listdir(basedir):
        fname = os.path.join(basedir, name)
        if os.path.isdir(fname):
            if files_changed(mtime, fname):
                return True

        if os.path.getmtime(fname) > mtime:
            log.info('Changed file detected: %s'%fname)
            return True
    
    return False


def build_less_bundle(name, intr, registry):
    cfg = registry.settings
    cache_dir = cfg['amd.tmpl-cache']

    node_path = cfg['amd.node']
    if not node_path:
        node_path = compat.NODE_PATH

    if not cfg['amd.tmpl-cache']:
        cfg['amd.tmpl-cache'] = tempfile.mkdtemp()

    debug = cfg['amd.debug']
    cache_dir = cfg['amd.tmpl-cache']

    bundle = None

    tname = 'less-%s'%name
    tpath = os.path.join(cache_dir, tname)
    if os.path.exists(tpath):
        # check for changes
        if (('md5' not in intr and
             files_changed(os.path.getmtime(tpath), intr['watchdir'])) or
            (debug and 
             files_changed(os.path.getmtime(tpath), intr['watchdir']))):
            log.info('Compiling less bundle: %s', name)
            bundle = compile_less(
                name, intr['abs_path'], node_path, cache_dir, not debug)

            with open(tpath, 'wb') as f:
                f.write(bundle)
        else:
            with open(tpath, 'rb') as f:
                bundle = f.read()
    else:
        log.info('Compiling less bundle: %s', name)
        bundle = compile_less(
            name, intr['abs_path'], node_path, cache_dir, not debug)
        with open(tpath, 'wb') as f:
            f.write(bundle)

    md5 = hashlib.md5()
    md5.update(bundle)
    intr['md5'] = md5.hexdigest()

    return bundle


@view_config(route_name='pyramid-less-bundle')
def view_bundle(request):
    name = request.matchdict['name']
    registry = request.registry

    storage = request.registry.get(ID_BUNDLE)
    if not storage or name not in storage:
        return HTTPNotFound()

    try:
        text = build_less_bundle(name, storage[name], request.registry)
    except Exception as err:
        return HTTPInternalServerError(str(err))

    response = request.response
    response.content_type = 'text/css'
    response.body = text
    return response


def less_bundle_url(request, name):
    storage = request.registry.get(ID_BUNDLE)
    if not storage or name not in storage:
        raise ValueError('less bundle is not found: %s' % name)

    intr = storage[name]
    if 'md5' not in intr:
        build_less_bundle(name, intr, request.registry)

    return request.route_url(
        'pyramid-less-bundle', name=name, _query={'_v': intr['md5']})
