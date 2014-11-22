# moment http://momentjs.com


def includeme(config):
    config.include('ptah.amdjs')

    # static assets
    config.add_static_view('_amdjs_moment/static', 'ptah.amdjs.moment:static/')

    config.add_amd_js(
        'moment', 'ptah.amdjs.moment:static/moment.min.js')
