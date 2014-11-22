# jquery http://jquery.org

def includeme(config):
    config.include('ptah.amdjs')

    # static assets
    config.add_static_view('_amdjs_jquery/static', 'ptah.amdjs.jquery:static/')
    
    config.add_amd_js(
        'jquery',
        'ptah.amdjs.jquery:static/jquery-1.9.1.min.js',
        'JQuery Library')

