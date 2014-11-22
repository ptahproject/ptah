import pytz
import ptah.form
import decimal, datetime
from ptah.jsfields import JSDateField, JSDateTimeField, CKEditorField


vocabulary = ptah.form.Vocabulary(
    (1, 'one', 'One', 'One description'),
    (2, 'two', 'Two', 'Two description'),
    (3, 'three', 'Three', 'Three description'))


@ptah.form.fieldpreview(ptah.form.MultiChoiceField)
def multiChoicePreview(request):
    field = ptah.form.MultiChoiceField(
        'MultiChoiceField',
        title = 'Multi choice field',
        description = 'Multi choice field preview description',
        default = [1,3],
        vocabulary = vocabulary)

    widget = field.bind(request, 'preview.', ptah.form.null, {})
    widget.update()
    return widget.render_widget()


@ptah.form.fieldpreview(ptah.form.ChoiceField)
def choicePreview(request):
    field = ptah.form.ChoiceField(
        'ChoiceField',
        title = 'Choice field',
        description = 'Choice field preview description',
        missing = 1,
        vocabulary = vocabulary)

    widget = field.bind(request, 'preview.', ptah.form.null, {})
    widget.update()
    return widget.render_widget()


@ptah.form.fieldpreview(ptah.form.BoolField)
def boolPreview(request):
    field = ptah.form.BoolField(
        'BoolField',
        default = True,
        title = 'Boolean field',
        description = 'Boolean field preview description')

    widget = field.bind(request, 'preview.', ptah.form.null, {})
    widget.update()
    return widget.render_widget()


@ptah.form.fieldpreview(ptah.form.RadioField)
def radioPreview(request):
    field = ptah.form.RadioField(
        'RadioField',
        title = 'Radio field',
        description = 'Radio field preview description',
        default = 1,
        vocabulary = vocabulary)

    widget = field.bind(request, 'preview.', ptah.form.null, {})
    widget.update()
    return widget.render_widget()


@ptah.form.fieldpreview(ptah.form.TextAreaField)
def textareaPreview(request):
    field = ptah.form.TextAreaField(
        'TextAreaField',
        title = 'TextArea field',
        description = 'TextArea field preview description',
        default = 'Test text in text area field.')

    widget = field.bind(request, 'preview.', ptah.form.null, {})
    widget.update()
    return widget.render_widget()


@ptah.form.fieldpreview(ptah.form.LinesField)
def linesPreview(request):
    field = ptah.form.LinesField(
        'LinesField',
        title = 'Lines field',
        description = 'Lines field preview description',
        default = ['One', 'Two', 'Three'])

    widget = field.bind(request, 'preview.', ptah.form.null, {})
    widget.update()
    return widget.render_widget()


@ptah.form.fieldpreview(ptah.form.TextField)
def textPreview(request):
    field = ptah.form.TextField(
        'TextField',
        title = 'Text field',
        description = 'Text field preview description',
        default = 'Test text in text field.')

    widget = field.bind(request, 'preview.', ptah.form.null, {})
    widget.update()
    return widget.render_widget()


@ptah.form.fieldpreview(ptah.form.FileField)
def filePreview(request):
    field = ptah.form.FileField(
        'FileField',
        title = 'File field',
        description = 'File field preview description',
        default = 'Test file in file field.')

    widget = field.bind(request, 'preview.', ptah.form.null, {})
    widget.update()
    return widget.render_widget()


@ptah.form.fieldpreview(ptah.form.IntegerField)
def intPreview(request):
    field = ptah.form.IntegerField(
        'IntegerField',
        title = 'Integer field',
        description = 'Integer field preview description',
        default = 456782)

    widget = field.bind(request, 'preview.', ptah.form.null, {})
    widget.update()
    return widget.render_widget()


@ptah.form.fieldpreview(ptah.form.FloatField)
def floatPreview(request):
    field = ptah.form.FloatField(
        'FloatField',
        title = 'Float field',
        description = 'Float field preview description',
        default = 456782.236)

    widget = field.bind(request, 'preview.', ptah.form.null, {})
    widget.update()
    return widget.render_widget()


@ptah.form.fieldpreview(ptah.form.DecimalField)
def decimalPreview(request):
    field = ptah.form.DecimalField(
        'DecimalField',
        title = 'Decimal field',
        description = 'Decimal field preview description',
        default = decimal.Decimal('10.54'))

    widget = field.bind(request, 'preview.', ptah.form.null, {})
    widget.update()
    return widget.render_widget()


@ptah.form.fieldpreview(ptah.form.PasswordField)
def passwordPreview(request):
    field = ptah.form.PasswordField(
        'PasswordField',
        title = 'Password field',
        description = 'Password field preview description')

    widget = field.bind(request, 'preview.', ptah.form.null, {})
    widget.update()
    return widget.render_widget()


@ptah.form.fieldpreview(JSDateField)
def jsdatePreview(request):
    field = JSDateField(
        'JSDateField',
        title = 'Bootstrap Date field',
        description = 'Bootstrap Date field preview description',
        default = datetime.date.today())

    widget = field.bind(request, 'preview.', ptah.form.null, {})
    widget.update()
    return widget.render_widget()


@ptah.form.fieldpreview(JSDateTimeField)
def jsdatetimePreview(request):
    field = JSDateTimeField(
        'JSDateTimeField',
        title = 'Bootstrap DateTime field',
        description = 'Bootstrap DateTime field preview description')

    widget = field.bind(request, 'preview.', datetime.datetime.now(), {})
    widget.update()
    return widget.render_widget()


@ptah.form.fieldpreview(CKEditorField)
def ckeditorPreview(request):
    field = CKEditorField(
        'CKEditorField',
        title = 'CKEditor field',
        description = 'CKEditor field preview description',
        default = 'Test text in ckeditor field.',
        width = '200px')

    widget = field.bind(request, 'preview.', ptah.form.null, {})
    widget.update()
    return widget.render_widget()


@ptah.form.fieldpreview(ptah.form.TimezoneField)
def timezonePreview(request):
    field = ptah.form.TimezoneField(
        'TimezoneField',
        title = 'Timezone field',
        description = 'Timezone field preview description',
        default = pytz.timezone('US/Central'))

    widget = field.bind(request, 'preview.', ptah.form.null, {})
    widget.update()
    return widget.render_widget()
