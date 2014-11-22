""" assets libraries """
from ptah.amdjs.compat import NODE_PATH


def includeme(config):
    # jquery http://jquery.org
    config.include('ptah.amdjs.jquery')

    # backbone http://backbonejs.org
    config.include('ptah.amdjs.backbone')

    # lodash https://github.com/amdjs/underscore
    config.include('ptah.amdjs.underscore')

    # json2
    config.include('ptah.amdjs.json2')

    # moment http://momentjs.com
    config.include('ptah.amdjs.moment')

    # bootstrap http://twitter.github.com/bootstrap/
    config.add_amd_js(
        'bootstrap', 'ptah.amdjs:static/bootstrap/bootstrap.min.js',
        'Twitter bootstrap javscript library', ('jquery',))
    config.add_amd_css(
        'bootstrap-css',
        'ptah.amdjs:static/bootstrap/bootstrap.min.css',
        'Twitter bootstrap javscript library')
    config.add_amd_css(
        'bootstrap-responsive-css',
        'ptah.amdjs:static/bootstrap/bootstrap-responsive.min.css',
        'Twitter bootstrap javscript library (Responsive)')

    # bootstrap http://getbootstrap.com
    config.include('ptah.amdjs.bootstrap')

    # handlebars http://handlebarsjs.com/
    config.include('ptah.amdjs.handlebarsjs')

    # pyramid
    config.include('ptah.amdjs.pyramidjs')
