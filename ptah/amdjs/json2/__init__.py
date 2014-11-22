# json2 https://github.com/douglascrockford/JSON-js


def includeme(config):
    config.include('ptah.amdjs')

    # static assets
    config.add_static_view('_amdjs_json2/static', 'ptah.amdjs.json2:static/')
    
    config.add_amd_js(
        'json2', 'ptah.amdjs.json2:static/json2.js')

