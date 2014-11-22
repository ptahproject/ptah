# ptah.amdjs


def includeme(cfg):
    from pyramid.settings import asbool, aslist
    from pyramid.interfaces import IStaticURLInfo
    from pyramid.compat import urlparse

    from ptah.amdjs import amd
    from ptah.amdjs.pstatic import StaticURLInfo

    # amdjs tween
    cfg.add_tween('ptah.amdjs.require.amdjs_tween_factory')

    def get_amdjs_data(request):
        return {'js': [], 'css': [], 'spec': '', 'fn': [], 'init': False}
    cfg.add_request_method(get_amdjs_data, 'amdjs_data', True, True)

    # static
    cfg.registry.registerUtility(StaticURLInfo(), IStaticURLInfo)

    # settings
    settings = cfg.get_settings()
    settings['amd.debug'] = asbool(settings.get('amd.debug', 't'))
    settings['amd.enabled'] = asbool(settings.get('amd.enabled', 't'))
    settings['amd.spec-dir'] = settings.get('amd.spec-dir', '').strip()
    settings['amd.tmpl-cache'] = settings.get('amd.tmpl-cache', '').strip()
    settings['amd.tmpl-langs'] = [
        s.strip() for s in aslist(settings.get('amd.tmpl-langs', ''))]
    settings['amd.node'] = settings.get('amd.node', '').strip()

    settings['static.url'] = settings.get('static.url', '').strip()
    settings['static.rewrite'] = asbool(settings.get('static.rewrite', 'f'))
    if not urlparse.urlparse(settings['static.url'])[0]:
        settings['static.rewrite'] = False
    else:
        if not settings['static.url'].endswith('/'):
            settings['static.url'] = '%s/' % settings['static.url']

    # spec settings
    specs = []
    for key, val in sorted(settings.items()):
        if key.startswith('amd.spec.'):
            specs.append((key[9:].strip(), val.strip()))

    settings['amd.spec'] = specs
    cfg.registry[amd.ID_AMD_SPEC] = {}

    # request methods
    cfg.add_request_method(amd.request_amd_init, 'init_amd')
    cfg.add_request_method(amd.request_includes, 'include_js')
    cfg.add_request_method(amd.request_css_includes, 'include_css')

    cfg.add_request_method(require.require_js, 'require')
    cfg.add_request_method(require.require_js, 'require_js')
    cfg.add_request_method(require.require_fn, 'require_fn')
    cfg.add_request_method(require.require_css, 'require_css')
    cfg.add_request_method(require.require_spec, 'require_spec')

    # config directives
    cfg.add_directive('add_amd_js', amd.add_js_module)
    cfg.add_directive('add_amd_css', amd.add_css_module)

    if settings['amd.debug']:
        from ptah.amdjs import amddebug
        settings['amd.debug.data'] = {
            'paths': [], 'cache': {}, 'mods': {}}

        cfg.registry[amd.ID_AMD_BUILD] = amddebug.build_init
        cfg.registry[amd.ID_AMD_BUILD_MD5] = amddebug.build_md5
        cfg.add_directive('add_amd_dir', amddebug.add_amd_dir)
    else:
        cfg.registry[amd.ID_AMD_BUILD] = amd.build_init
        cfg.registry[amd.ID_AMD_BUILD_MD5] = amd.build_md5
        cfg.add_directive('add_amd_dir', amd.add_amd_dir)

    cfg.registry[amd.ID_AMD_MD5] = {}

    # amd init route
    cfg.add_route('pyramid-amd-init', '/_amd_{specname}.js')

    # static assets
    cfg.add_static_view('_amdjs/static', 'ptah.amdjs:static/')

    # handlebars bundle
    from .handlebars import register_handlebars_bundle

    cfg.add_directive(
        'add_hb_bundle', register_handlebars_bundle)
    cfg.add_directive(
        'add_handlebars_bundle', register_handlebars_bundle)
    cfg.add_route(
        'pyramid-hb-bundle', '/_handlebars/{name}.js')

    # less bundle
    from .less import register_less_bundle, less_bundle_url

    cfg.add_directive(
        'add_less_bundle', register_less_bundle)
    cfg.add_route(
        'pyramid-less-bundle', '/_amd_less/{name}')

    cfg.add_request_method(less_bundle_url, 'less_bundle_url')

    # scan
    cfg.scan('ptah.amdjs')

    # init amd specs
    amd.init_amd_spec(cfg)
