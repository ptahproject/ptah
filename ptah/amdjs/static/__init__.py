""" assets libraries """
from ptah.amdjs.compat import NODE_PATH


def includeme(config):
    # backbone http://backbonejs.org
    config.include('ptah.amdjs.backbone')

    # lodash https://github.com/amdjs/underscore
    config.include('ptah.amdjs.underscore')

    # json2
    config.include('ptah.amdjs.json2')

    # handlebars http://handlebarsjs.com/
    config.include('ptah.amdjs.handlebarsjs')

    # pyramid
    config.include('ptah.amdjs.pyramidjs')
