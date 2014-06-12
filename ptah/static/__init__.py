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
        'bootstrap3-datetimepicker', 'ptah:static/bootstrap3/datetimepicker/js/bootstrap-datetimepicker.min.js',
        'Bootstrap3 Datetimepicker', ('jquery', 'bootstrap3'))

    config.add_amd_css(
        'bootstrap3-datetimepicker-css', 'ptah:static/bootstrap3/datetimepicker/css/bootstrap-datetimepicker.min.css',
        'Bootstrap3 Datetimepicker')

    config.add_amd_js(
        'ckeditor', 'ptah:static/ckeditor/ckeditor.js',
        'CKEditor', ('jquery',))

    config.add_amd_css(
        'bootstrap3-navbar-css',
        'ptah:static/bootstrap3/navbar.css',
        'Twitter bootstrap navbar extension')
