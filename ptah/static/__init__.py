""" assets libraries """
import ptah

def includeme(config):
    # amd modules
    config.register_amd_module(
        'jquery', 'ptah:static/jquery/jquery-1.8.2.min.js',
        'JQuery Library')
    config.register_amd_module(
        'jquery-ui', 'ptah:static/jquery/jquery-ui-1.9.0.min.js',
        'JQuery UI Library', ('jquery',))
    config.register_amd_module(
        'jquery-ui-css', 'ptah:static/jquery/jquery-ui-1.9.0.min.css',
        'JQuery UI Library')

    config.register_amd_module(
        'sockjs', 'ptah:static/lib/sockjs-0.3.2.min.js',
        'SockJS Client library')
    config.register_amd_module(
        'underscore', 'ptah:static/lib/underscore-min.js')
    config.register_amd_module(
        'handlebars', 'ptah:static/lib/handlebars.runtime.js',
        'Handlebars runtime library')
    config.register_amd_module(
        'bootstrap', 'ptah:static/bootstrap/bootstrap.min.js',
        'Twitter bootstrap javscript library', ('jquery',))
    config.register_amd_module(
        'bootstrap-css', 
        'ptah:static/bootstrap/bootstrap.min.css',
        'Twitter bootstrap javscript library')
    config.register_amd_module(
        'bootstrap-responsive-css',
        'ptah:static/bootstrap/bootstrap-responsive.min.css',
        'Twitter bootstrap javscript library (Responsive)')

    config.register_amd_module(
        'ckeditor', 'ptah:static/ckeditor/ckeditor.js',
        'CKEditor', ('jquery',))

    # ptah
    config.register_amd_module(
        'ptah', 'ptah:static/ptah.js', 'Ptah', ('handlebars','sockjs','jquery'))
    config.register_amd_module(
        'ptah-date-format', 'ptah:static/date-format.js',
        require=('jquery', 'handlebars'))

    # ptah ui classes
    config.register_amd_module(
        'ptah-form', 'ptah:static/form.js',
        require=('jquery', 'ptah', 'ptah-templates', 'bootstrap'))
    config.register_amd_module(
        'ptah-pager', 'ptah:static/pager.js',
        require=('jquery', 'ptah', 'ptah-templates'))

    # templates
    config.register_mustache_bundle(
        'ptah-templates', 'ptah:templates/mustache/', i18n_domain='ptah')
