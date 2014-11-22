# underscore https://github.com/amdjs/underscore


def includeme(config):
    config.include('ptah.amdjs')

    # static assets
    config.add_static_view('_amdjs_underscore/static', 'ptah.amdjs.underscore:static/')
    
    config.add_amd_js(
        'underscore', 'ptah.amdjs.underscore:static/underscore-min.js')

