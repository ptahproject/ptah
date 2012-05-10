""" assets libraries """
import ptah

def includeme(config):
    # amd modules
    config.register_amd_module(
        'jquery', 'ptah:static/jquery/jquery-1.7.2.min.js',
        'JQuery Library')
    config.register_amd_module(
        'jquery-ui', 'ptah:static/jquery/jquery-ui-1.8.20.min.js',
        'JQuery UI Library')
    config.register_amd_module(
        'sockjs', 'ptah:static/lib/sockjs-0.3.1.min.js',
        'SockJS Client library')
    config.register_amd_module(
        'underscore', 'ptah:static/lib/underscore-1.3.1.js')
    config.register_amd_module(
        'handlebars', 'ptah:static/lib/handlebars.runtime.js',
        'Handlebars runtime library')
    config.register_amd_module(
        'bootstrap', 'ptah:static/bootstrap/bootstrap.min.js',
        'Twitter bootstrap javscript library')
    config.register_amd_module(
        'ckeditor', 'ptah:static/ckeditor/ckeditor.js',
        'CKEditor')

    # ptah
    config.register_amd_module(
        'ptah', 'ptah:static/ptah.js')
    config.register_amd_module(
        'ptah-date-format', 'ptah:static/date-format.js')

    # ptah ui classes
    config.register_amd_module(
        'ptah-form', 'ptah:static/form.js')
    config.register_amd_module(
        'ptah-pager', 'ptah:static/pager.js')

    # templates
    config.register_mustache_bundle(
        'ptah-templates', 'ptah:templates/mustache/')


# jQuery library
ptah.library(
    'jquery-ui',
    'ptah:static/jquery/jquery-ui-1.8.20.css',
    type='css')

# Bootstrap css
ptah.library(
    'bootstrap',
    path='ptah:static/bootstrap/bootstrap.min.css',
    type="css")


# curl
ptah.library(
    'curl',
    path='ptah:static/lib/curl-0.6.2.js',
    type="js")

ptah.library(
    'curl-debug',
    path='ptah:static/lib/curl-debug.js',
    type="js")
