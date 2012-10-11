""" assets libraries """
import ptah

def includeme(config):
    # amd modules
    config.add_amd_module(
        'jquery-ui', 'ptah:static/jquery/jquery-ui-1.9.0.min.js',
        'JQuery UI Library', ('jquery',))
    config.add_amd_module(
        'jquery-ui-css', 'ptah:static/jquery/jquery-ui-1.9.0.min.css',
        'JQuery UI Library')

    config.add_amd_module(
        'sockjs', 'ptah:static/lib/sockjs-0.3.2.min.js',
        'SockJS Client library')
    config.add_amd_module(
        'bootstrap', 'ptah:static/bootstrap/bootstrap.min.js',
        'Twitter bootstrap javscript library', ('jquery',))
    config.add_amd_module(
        'bootstrap-css', 
        'ptah:static/bootstrap/bootstrap.min.css',
        'Twitter bootstrap javscript library')
    config.add_amd_module(
        'bootstrap-responsive-css',
        'ptah:static/bootstrap/bootstrap-responsive.min.css',
        'Twitter bootstrap javscript library (Responsive)')

    config.add_amd_module(
        'ckeditor', 'ptah:static/ckeditor/ckeditor.js',
        'CKEditor', ('jquery',))

    # ptah
    config.add_amd_module(
        'ptah', 'ptah:static/ptah.js', 'Ptah', ('handlebars','sockjs','jquery'))
    config.add_amd_module(
        'ptah-date-format', 'ptah:static/date-format.js',
        require=('jquery', 'handlebars'))

    # ptah ui classes
    config.add_amd_module(
        'ptah-form', 'ptah:static/form.js',
        require=('jquery', 'ptah', 'ptah-templates', 'bootstrap'))
    config.add_amd_module(
        'ptah-pager', 'ptah:static/pager.js',
        require=('jquery', 'ptah', 'ptah-templates'))

    # templates
    config.add_mustache_bundle(
        'ptah-templates', 'ptah:templates/mustache/', i18n_domain='ptah')
