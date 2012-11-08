import pytz
import pform
import decimal, datetime
from ptah.jsfields import JSDateField, JSDateTimeField, CKEditorField


vocabulary = pform.SimpleVocabulary.from_items(
    (1, 'one', 'One', 'One description'),
    (2, 'two', 'Two', 'Two description'),
    (3, 'three', 'Three', 'Three description'))


@pform.fieldpreview(pform.MultiChoiceField)
def multiChoicePreview(request):
    field = pform.MultiChoiceField(
        'MultiChoiceField',
        title = 'Multi choice field',
        description = 'Multi choice field preview description',
        default = [1,3],
        vocabulary = vocabulary)

    widget = field.bind(request, 'preview.', pform.null, {})
    widget.update()
    return widget.render_widget()


@pform.fieldpreview(pform.ChoiceField)
def choicePreview(request):
    field = pform.ChoiceField(
        'ChoiceField',
        title = 'Choice field',
        description = 'Choice field preview description',
        missing = 1,
        vocabulary = vocabulary)

    widget = field.bind(request, 'preview.', pform.null, {})
    widget.update()
    return widget.render_widget()


@pform.fieldpreview(pform.BoolField)
def boolPreview(request):
    field = pform.BoolField(
        'BoolField',
        default = True,
        title = 'Boolean field',
        description = 'Boolean field preview description')

    widget = field.bind(request, 'preview.', pform.null, {})
    widget.update()
    return widget.render_widget()


@pform.fieldpreview(pform.RadioField)
def radioPreview(request):
    field = pform.RadioField(
        'RadioField',
        title = 'Radio field',
        description = 'Radio field preview description',
        default = 1,
        vocabulary = vocabulary)

    widget = field.bind(request, 'preview.', pform.null, {})
    widget.update()
    return widget.render_widget()


@pform.fieldpreview(pform.TextAreaField)
def textareaPreview(request):
    field = pform.TextAreaField(
        'TextAreaField',
        title = 'TextArea field',
        description = 'TextArea field preview description',
        default = 'Test text in text area field.')

    widget = field.bind(request, 'preview.', pform.null, {})
    widget.update()
    return widget.render_widget()


@pform.fieldpreview(pform.LinesField)
def linesPreview(request):
    field = pform.LinesField(
        'LinesField',
        title = 'Lines field',
        description = 'Lines field preview description',
        default = ['One', 'Two', 'Three'])

    widget = field.bind(request, 'preview.', pform.null, {})
    widget.update()
    return widget.render_widget()


@pform.fieldpreview(pform.TextField)
def textPreview(request):
    field = pform.TextField(
        'TextField',
        title = 'Text field',
        description = 'Text field preview description',
        default = 'Test text in text field.')

    widget = field.bind(request, 'preview.', pform.null, {})
    widget.update()
    return widget.render_widget()


@pform.fieldpreview(pform.IntegerField)
def intPreview(request):
    field = pform.IntegerField(
        'IntegerField',
        title = 'Integer field',
        description = 'Integer field preview description',
        default = 456782)

    widget = field.bind(request, 'preview.', pform.null, {})
    widget.update()
    return widget.render_widget()


@pform.fieldpreview(pform.FloatField)
def floatPreview(request):
    field = pform.FloatField(
        'FloatField',
        title = 'Float field',
        description = 'Float field preview description',
        default = 456782.236)

    widget = field.bind(request, 'preview.', pform.null, {})
    widget.update()
    return widget.render_widget()


@pform.fieldpreview(pform.DecimalField)
def decimalPreview(request):
    field = pform.DecimalField(
        'DecimalField',
        title = 'Decimal field',
        description = 'Decimal field preview description',
        default = decimal.Decimal('10.54'))

    widget = field.bind(request, 'preview.', pform.null, {})
    widget.update()
    return widget.render_widget()


@pform.fieldpreview(pform.PasswordField)
def passwordPreview(request):
    field = pform.PasswordField(
        'PasswordField',
        title = 'Password field',
        description = 'Password field preview description')

    widget = field.bind(request, 'preview.', pform.null, {})
    widget.update()
    return widget.render_widget()


@pform.fieldpreview(JSDateField)
def jsdatePreview(request):
    field = JSDateField(
        'JSDateField',
        title = 'jQuery Date field',
        description = 'jQuery Date field preview description',
        default = datetime.date.today())

    widget = field.bind(request, 'preview.', pform.null, {})
    widget.update()
    return widget.render_widget()


@pform.fieldpreview(JSDateTimeField)
def jsdatetimePreview(request):
    field = JSDateTimeField(
        'JSDateTimeField',
        title = 'jQuery DateTime field',
        description = 'jQuery DateTime field preview description')

    widget = field.bind(request, 'preview.', datetime.datetime.now(), {})
    widget.update()
    return widget.render_widget()


@pform.fieldpreview(CKEditorField)
def ckeditorPreview(request):
    field = CKEditorField(
        'CKEditorField',
        title = 'CKEditor field',
        description = 'CKEditor field preview description',
        default = 'Test text in ckeditor field.',
        width = '200px')

    widget = field.bind(request, 'preview.', pform.null, {})
    widget.update()
    return widget.render_widget()


@pform.fieldpreview(pform.TimezoneField)
def timezonePreview(request):
    field = pform.TimezoneField(
        'TimezoneField',
        title = 'Timezone field',
        description = 'Timezone field preview description',
        default = pytz.timezone('US/Central'))

    widget = field.bind(request, 'preview.', pform.null, {})
    widget.update()
    return widget.render_widget()
