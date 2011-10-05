""" TineMCE field """
from memphis import view, form


# TinyMCE
view.static(
    'tiny_mce', 'ptah_app:static/tiny_mce')


view.library(
    "tiny_mce",
    resource="tiny_mce",
    path=('tiny_mce.js', 'jquery.tinymce.js'),
    type="js",
    require='jquery')


class TinymceField(form.TextAreaField):
    __doc__ = u'TinyMCE Text Area input widget'

    form.field('tinymce')

    klass = u'tinymce-widget'

    width = '400px'
    height = '300px'
    theme = "advanced"

    tmpl_input = view.template(
        "ptah_app:templates/tinymce_input.pt")
