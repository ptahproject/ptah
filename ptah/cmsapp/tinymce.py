""" TineMCE field """
from ptah import view, form


# TinyMCE
view.static(
    'tiny_mce', 'ptah.cmsapp:static/tiny_mce')


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
        "ptah.cmsapp:templates/tinymce_input.pt")


@form.fieldpreview(TinymceField)
def tinemcePreview(request):
    field = TinymceField(
        'TinymceField',
        title = 'TinyMCE field',
        description = 'TinyMCE field preview description',
        default = 'Test text in tinymce field.',
        width = '200px')

    widget = field.bind('preview.', form.null, {})
    widget.update(request)
    return widget.snippet('form-widget', widget)
