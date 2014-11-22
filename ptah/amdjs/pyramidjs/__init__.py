# pyramid and handlebarhelpers


def includeme(config):
    config.include('ptah.amdjs')

    # static assets
    config.add_static_view('_amdjs_pyramidjs/static', 'ptah.amdjs.pyramidjs:static/')
    
    config.add_amd_js(
        'pyramid', 'ptah.amdjs.pyramidjs:static/pyramid.js',
        'Pyramid amdjs', ('backbone',))

    # handlebars support helper
    config.add_amd_js(
        'pyramid:templates', 'ptah.amdjs.pyramidjs:static/templates.js',
        'Handlebars templates', ('handlebars',))

    # handlebars datetime helper
    config.add_amd_js(
        'pyramid:datetime', 'ptah.amdjs.pyramidjs:static/datetime.js',
        'Datetime handlebars helper', ('handlebars', 'moment'))

