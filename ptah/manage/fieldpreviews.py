import pytz
import decimal, datetime

from ptah import form


vocabulary = form.SimpleVocabulary.from_items(
    (1, 'one', 'One', 'One description'),
    (2, 'two', 'Two', 'Two description'),
    (3, 'three', 'Three', 'Three description'))


@form.fieldpreview(form.MultiChoiceField)
def multiChoicePreview(request):
    field = form.MultiChoiceField(
        'MultiChoiceField',
        title = 'Multi choice field',
        description = 'Multi choice field preview description',
        default = [1,3],
        vocabulary = vocabulary)

    widget = field.bind('preview.', form.null, {})
    widget.update(request)
    return widget.snippet('form-widget', widget)


@form.fieldpreview(form.ChoiceField)
def choicePreview(request):
    field = form.ChoiceField(
        'ChoiceField',
        title = 'Choice field',
        description = 'Choice field preview description',
        missing = 1,
        vocabulary = vocabulary)

    widget = field.bind('preview.', form.null, {})
    widget.update(request)
    return widget.snippet('form-widget', widget)


@form.fieldpreview(form.BoolField)
def boolPreview(request):
    field = form.BoolField(
        'BoolField',
        default = True,
        title = 'Boolean field',
        description = 'Boolean field preview description')

    widget = field.bind('preview.', form.null, {})
    widget.update(request)
    return widget.snippet('form-widget', widget)


@form.fieldpreview(form.RadioField)
def radioPreview(request):
    field = form.RadioField(
        'RadioField',
        title = 'Radio field',
        description = 'Radio field preview description',
        default = 1,
        vocabulary = vocabulary)

    widget = field.bind('preview.', form.null, {})
    widget.update(request)
    return widget.snippet('form-widget', widget)


@form.fieldpreview(form.TextAreaField)
def textareaPreview(request):
    field = form.TextAreaField(
        'TextAreaField',
        title = 'TextArea field',
        description = 'TextArea field preview description',
        default = 'Test text in text area field.')

    widget = field.bind('preview.', form.null, {})
    widget.update(request)
    return widget.snippet('form-widget', widget)


@form.fieldpreview(form.LinesField)
def linesPreview(request):
    field = form.LinesField(
        'LinesField',
        title = 'Lines field',
        description = 'Lines field preview description',
        default = ['One', 'Two', 'Three'])

    widget = field.bind('preview.', form.null, {})
    widget.update(request)
    return widget.snippet('form-widget', widget)


@form.fieldpreview(form.TextField)
def textPreview(request):
    field = form.TextField(
        'TextField',
        title = 'Text field',
        description = 'Text field preview description',
        default = 'Test text in text field.')

    widget = field.bind('preview.', form.null, {})
    widget.update(request)
    return widget.snippet('form-widget', widget)


@form.fieldpreview(form.IntegerField)
def intPreview(request):
    field = form.IntegerField(
        'IntegerField',
        title = 'Integer field',
        description = 'Integer field preview description',
        default = 456782)

    widget = field.bind('preview.', form.null, {})
    widget.update(request)
    return widget.snippet('form-widget', widget)


@form.fieldpreview(form.FloatField)
def floatPreview(request):
    field = form.FloatField(
        'FloatField',
        title = 'Float field',
        description = 'Float field preview description',
        default = 456782.236)

    widget = field.bind('preview.', form.null, {})
    widget.update(request)
    return widget.snippet('form-widget', widget)


@form.fieldpreview(form.DecimalField)
def decimalPreview(request):
    field = form.DecimalField(
        'DecimalField',
        title = 'Decimal field',
        description = 'Decimal field preview description',
        default = decimal.Decimal('10.54'))

    widget = field.bind('preview.', form.null, {})
    widget.update(request)
    return widget.snippet('form-widget', widget)


@form.fieldpreview(form.PasswordField)
def passwordPreview(request):
    field = form.PasswordField(
        'PasswordField',
        title = 'Password field',
        description = 'Password field preview description')

    widget = field.bind('preview.', form.null, {})
    widget.update(request)
    return widget.snippet('form-widget', widget)


@form.fieldpreview(form.JSDateField)
def jsdatePreview(request):
    field = form.JSDateField(
        'JSDateField',
        title = 'jQuery Date field',
        description = 'jQuery Date field preview description',
        default = datetime.date.today())

    widget = field.bind('preview.', form.null, {})
    widget.update(request)
    return widget.snippet('form-widget', widget)


@form.fieldpreview(form.JSDateTimeField)
def jsdatetimePreview(request):
    field = form.JSDateTimeField(
        'JSDateTimeField',
        title = 'jQuery DateTime field',
        description = 'jQuery DateTime field preview description')

    widget = field.bind('preview.', datetime.datetime.now(), {})
    widget.update(request)
    return widget.snippet('form-widget', widget)


@form.fieldpreview(form.TinymceField)
def tinemcePreview(request):
    field = form.TinymceField(
        'TinymceField',
        title = 'TinyMCE field',
        description = 'TinyMCE field preview description',
        default = 'Test text in tinymce field.',
        width = '200px')

    widget = field.bind('preview.', form.null, {})
    widget.update(request)
    return widget.snippet('form-widget', widget)


@form.fieldpreview(form.TimezoneField)
def timezonePreview(request):
    field = form.TimezoneField(
        'TimezoneField',
        title = 'Timezone field',
        description = 'Timezone field preview description',
        default = pytz.timezone('US/Central'))

    widget = field.bind('preview.', form.null, {})
    widget.update(request)
    return widget.snippet('form-widget', widget)
