""" assets libraries """


def includeme(config):
    # amd modules
    config.add_amd_js(
        'jquery-ui', 'ptah:static/jquery/jquery-ui-1.10.0.custom.min.js',
        'JQuery UI Library', ('jquery',))
    config.add_amd_css(
        'jquery-ui.css', 'ptah:static/jquery/jquery-ui-1.10.0.custom.min.css',
        'JQuery UI Library')

    config.add_amd_js(
        'ckeditor', 'ptah:static/ckeditor/ckeditor.js',
        'CKEditor', ('jquery',))

    config.add_amd_css(
        'bootstrap3-navbar-css',
        'ptah:static/bootstrap3/navbar.css',
        'Twitter bootstrap navbar extension')
