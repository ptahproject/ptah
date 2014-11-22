# backbone http://backbonejs.org


def includeme(config):
    config.include('ptah.amdjs')

    # static assets
    config.add_static_view('_amdjs_backbone/static', 'ptah.amdjs.backbone:static/')
    
    config.add_amd_js(
        'backbone', 'ptah.amdjs.backbone:static/backbone-min.js')

