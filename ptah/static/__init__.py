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
        'ckeditor', 'ptah:static/ckeditor/ckeditor.js',
        'CKEditor', ('jquery',))

    # ptah ui classes
    config.add_amd_js(
        'ptah-form', 'ptah:static/form.js',
        requires=('jquery', 'pyramid', 'ptah-templates', 'bootstrap'))
    config.add_amd_js(
        'ptah-pager', 'ptah:static/pager.js',
        requires=('jquery', 'pyramid', 'ptah-templates'))

    # templates
    config.add_handlebars_bundle(
        'ptah-templates', 'ptah:templates/mustache/', i18n_domain='ptah')
