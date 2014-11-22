# handlebars http://handlebarsjs.com/
from ptah.amdjs.compat import NODE_PATH

def includeme(config):
    config.include('ptah.amdjs')

    # static assets
    config.add_static_view('_amdjs_handlebars/static', 'ptah.amdjs.handlebarsjs:static/')

    node_path = config.get_settings()['amd.node']
    if not node_path:
        node_path = NODE_PATH
    if not node_path:
        config.add_amd_js(
            'handlebars', 'ptah.amdjs.handlebarsjs:static/handlebars.js',
            'Handlebars library')
    else:
        config.add_amd_js(
            'handlebars', 'ptah.amdjs.handlebarsjs:static/handlebars.runtime.js',
            'Handlebars runtime library')
