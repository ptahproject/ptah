""" assets libraries """


def includeme(config):
    # amd modules
    config.add_amd_js(
        'jquery-ui', 'ptah:static/jquery/jquery-ui-1.9.0.min.js',
        'JQuery UI Library', ('jquery',))
    config.add_amd_css(
        'jquery-ui-css', 'ptah:static/jquery/jquery-ui-1.9.0.min.css',
        'JQuery UI Library')

    config.add_amd_js(
        'bootstrap', 'ptah:static/bootstrap/bootstrap.min.js',
        'Twitter bootstrap javscript library', ('jquery',))
    config.add_amd_css(
        'bootstrap-css',
        'ptah:static/bootstrap/bootstrap.min.css',
        'Twitter bootstrap javscript library')
    config.add_amd_css(
        'bootstrap-responsive-css',
        'ptah:static/bootstrap/bootstrap-responsive.min.css',
        'Twitter bootstrap javscript library (Responsive)')

    config.add_amd_js(
        'ckeditor', 'ptah:static/ckeditor/ckeditor.js',
        'CKEditor', ('jquery',))

    # ptah
    config.add_amd_js(
        'ptah-date-format', 'ptah:static/date-format.js',
        requires=('jquery', 'handlebars'))

    # ptah ui classes
    config.add_amd_js(
        'ptah-form', 'ptah:static/form.js',
        requires=('jquery', 'pyramid', 'ptah-templates', 'bootstrap'))
    config.add_amd_js(
        'ptah-pager', 'ptah:static/pager.js',
        requires=('jquery', 'pyramid', 'ptah-templates'))

    # templates
    config.add_mustache_bundle(
        'ptah-templates', 'ptah:templates/mustache/', i18n_domain='ptah')
