""" Basic fields """
import pytz
import datetime
import decimal

from ptah import view
from ptah.form import iso8601
from ptah.form import vocabulary
from ptah.form.field import field, Field
from ptah.form.interfaces import _, null, Invalid, ITerm


class InputField(Field, view.View):

    title = None
    lang = None
    disabled = None
    tabindex = None
    lang = None
    disabled = None
    readonly = None
    alt = None
    accesskey = None
    size = None
    maxlength = None

    tmpl_input = "ptah.form:templates/fields/text-input.pt"
    tmpl_display = "ptah.form:templates/fields/text-display.pt"

    def serialize(self, value):
        return value

    def deserialize(self, value):
        return value

    def update(self, request):
        super(InputField, self).update(request)

        if self.readonly:
            self.add_css_class('disabled')

    def add_css_class(self, css):
        self.klass = ('%s %s' % (self.klass or '', css)).strip()


class VocabularyField(InputField):

    vocabulary = None
    noValueToken = '--NOVALUE--'

    def __init__(self, name, **kw):
        super(VocabularyField, self).__init__(name, **kw)

        if self.vocabulary is None:
            raise ValueError("Vocabulary is not specified.")

    def is_checked(self, term):
        raise NotImplementedError()

    def update_items(self):
        self.items = []
        for count, term in enumerate(self.vocabulary):
            checked = self.is_checked(term)
            id = '%s-%i' % (self.id, count)
            label = term.token
            desc = None
            if ITerm.providedBy(term):
                label = term.title if term.title is not None else term.token
                desc = term.description
            self.items.append(
                {'id': id, 'name': self.name, 'value': term.token,
                 'label': label, 'description': desc, 'checked': checked})


class BaseChoiceField(VocabularyField):
    """ choice field """

    tmpl_display = "ptah.form:templates/fields/basechoice-display.pt"

    def serialize(self, value):
        if value is null:
            return null

        try:
            return self.vocabulary.get_term(value).token
        except Exception:
            raise Invalid(
                self, _('"${val}" is not in vocabulary',
                        mapping={'val': value}))

    def deserialize(self, value):
        if not value:
            return null

        try:
            return self.vocabulary.get_term_bytoken(value).value
        except Exception:
            raise Invalid(
                self, _('"${val}" is not in vocabulary',
                        mapping={'val': value}))

    def extract(self, default=null):
        value = self.params.get(self.name, default)
        if value is default:
            return default

        if value == self.noValueToken:
            return default

        return value

    def is_checked(self, term):
        return term.token == self.form_value

    def update(self, request):
        super(BaseChoiceField, self).update(request)

        self.update_items()


class BaseMultiChoiceField(VocabularyField):
    """ multi choice field """

    tmpl_display = "ptah.form:templates/fields/basemultichoice-display.pt"

    def serialize(self, value):
        if value is null:
            return null
        try:
            res = []
            for val in value:
                res.append(self.vocabulary.get_term(val).token)
            return res
        except (LookupError, TypeError):
            raise Invalid(
                self, _('"${val}" is not in vocabulary',
                        mapping={'val': value}))

    def deserialize(self, value):
        if not value:
            return null
        try:
            res = []
            for val in value:
                res.append(self.vocabulary.get_term_bytoken(val).value)
            return res
        except Exception:
            raise Invalid(
                self, _('"${val}" is not in vocabulary',
                        mapping={'val': value}))

    def extract(self, default=null):
        if self.name not in self.params:
            return default

        value = []
        tokens = self.params.getall(self.name)
        for token in tokens:
            if token == self.noValueToken:
                continue

            value.append(token)

        return value

    def is_checked(self, term):
        return term.token in self.form_value

    def update(self, request):
        super(BaseMultiChoiceField, self).update(request)

        if self.form_value in (null, None):
            self.form_value = []

        self.update_items()


@field('text')
class TextField(InputField):
    __doc__ = _('HTML Text input widget')

    klass = 'text-widget'
    value = ''

    def loads(self, s):
        if not s.startswith('"'):
            s = '"{0}"'.format(s)

        return super(TextField, self).loads(s)


class Number(object):

    num = None

    def serialize(self, value):
        if value is null:
            return null

        try:
            return str(self.num(value))
        except Exception:
            raise Invalid(self,
                          _('"${val}" is not a number',
                            mapping={'val': value}),
                          )

    def deserialize(self, value):
        if value != 0 and not value:
            return null

        try:
            return self.num(value)
        except Exception:
            raise Invalid(
                self, _('"${val}" is not a number', mapping={'val': value}))


@field('int')
class IntegerField(Number, InputField):
    __doc__ = _('Integer input widget')

    num = int
    value = 0
    klass = 'int-widget'


@field('float')
class FloatField(Number, InputField):
    __doc__ = _('Float input widget')

    num = float
    klass = 'float-widget'


@field('decimal')
class DecimalField(Number, InputField):
    __doc__ = _('Decimal input widget')

    klass = 'decimal-widget'

    def num(self, val):
        return decimal.Decimal(str(val))


@field('textarea')
class TextAreaField(TextField):
    __doc__ = _('HTML Text Area input widget')

    klass = 'textarea-widget'
    value = ''

    rows = 5
    cols = 40

    tmpl_input = "ptah.form:templates/fields/textarea-input.pt"


@field('file')
class FileField(TextField):
    __doc__ = _('HTML File input widget')

    klass = 'input-file'

    tmpl_input = "ptah.form:templates/fields/file-input.pt"

    def extract(self, default=null):
        value = self.params.get(self.name, default)

        if hasattr(value, 'file'):
            data = {}
            data['fp'] = value.file
            data['filename'] = value.filename
            data['mimetype'] = value.type
            data['size'] = value.length
            return data

        return default


@field('lines')
class LinesField(TextAreaField):
    __doc__ = _('Text area based widget, each line is treated as '
                'sequence element.')

    klass = 'textlines-widget'

    loads = Field.loads

    def serialize(self, value):
        if value is null or not value:
            return null

        try:
            return '\n'.join(value)
        except Exception:
            raise Invalid(self,
                          _('"${val}" is not a list',
                            mapping={'val': value}),
                          )

    def deserialize(self, value):
        if not value:
            return null

        try:
            return [s.strip() for s in value.split()]
        except Exception:
            raise Invalid(self,
                          _('"${val}" is not a list',
                            mapping={'val': value}),
                          )


@field('password')
class PasswordField(TextField):
    __doc__ = _('HTML Password input widget.')

    klass = 'password-widget'

    tmpl_input = "ptah.form:templates/fields/password-input.pt"
    tmpl_display = "ptah.form:templates/fields/password-display.pt"


@field('multichoice')
class MultiChoiceField(BaseMultiChoiceField):
    __doc__ = _('HTML Checkboxs input based widget.')

    klass = 'multichoice-widget'
    tmpl_input = "ptah.form:templates/fields/multichoice-input.pt"


class DateField(TextField):
    __doc__ = _('Simple date input field.')

    tmpl_display = "ptah.form:templates/fields/date-display.pt"

    def serialize(self, value):
        if value is null:
            return null

        if isinstance(value, datetime.datetime):
            value = value.date()

        if not isinstance(value, datetime.date):
            raise Invalid(self,
                          _('"${val}" is not a date object',
                            mapping={'val': value}))

        return value.isoformat()

    def deserialize(self, value):
        if not value:
            return null

        try:
            result = iso8601.parse_date(value)
            result = result.date()
        except (iso8601.ParseError, TypeError):
            try:
                year, month, day = map(int, value.split('-', 2))
                result = datetime.date(year, month, day)
            except Exception as e:
                raise Invalid(
                    self, _('Invalid date', mapping={'val': value, 'err': e}))

        return result


class DateTimeField(TextField):

    default_tzinfo = iso8601.Utc()

    tmpl_display = "ptah.form:templates/fields/datetime-display.pt"

    def serialize(self, value):
        if value is null or value is None or not value:
            return null

        if type(value) is datetime.date:  # cannot use isinstance; dt subs date
            value = datetime.datetime.combine(value, datetime.time())

        if not isinstance(value, datetime.datetime):
            raise Invalid(
                self, _('"${val}" is not a datetime object',
                        mapping={'val': value}))

        if value.tzinfo is None:
            value = value.replace(tzinfo=self.default_tzinfo)

        return value.isoformat()

    def deserialize(self, value):
        if not value:
            return null

        try:
            result = iso8601.parse_date(
                value, default_timezone=self.default_tzinfo)
        except (iso8601.ParseError, TypeError) as e:
            try:
                year, month, day = map(int, value.split('-', 2))
                result = datetime.datetime(year, month, day,
                                           tzinfo=self.default_tzinfo)
            except Exception as e:
                raise Invalid(self, _('Invalid date',
                                      mapping={'val': value, 'err': e}))
        return result


@field('radio')
class RadioField(BaseChoiceField):
    __doc__ = _('HTML Radio input widget.')

    klass = 'radio-widget'
    tmpl_input = "ptah.form:templates/fields/radio-input.pt"


@field('bool')
class BoolField(BaseChoiceField):
    __doc__ = _('Boolean input widget.')

    vocabulary = vocabulary.SimpleVocabulary.from_items(
        (True, 'true',  _('yes')),
        (False, 'false',  _('no')))

    tmpl_input = "ptah.form:templates/fields/bool-input.pt"


@field('choice')
class ChoiceField(BaseChoiceField):
    __doc__ = _('HTML Select input widget.')

    size = 1
    klass = 'select-widget'
    multiple = None
    promptMessage = _('select a value ...')

    tmpl_input = "ptah.form:templates/fields/select-input.pt"

    def update_items(self):
        super(ChoiceField, self).update_items()

        if not self.required:
            self.items.insert(0, {
                    'id': self.id + '-novalue',
                    'name': self.name,
                    'value': self.noValueToken,
                    'label': self.promptMessage,
                    'checked': self.form_value is null,
                    'description': '',
                    })


@field('multiselect')
class MultiSelectField(ChoiceField):
    __doc__ = _('HTML Multi Select input widget.')

    size = 5
    multiple = 'multiple'


class TimezoneField(ChoiceField):
    """ timezone field """

    _tzs = dict((str(tz).lower(), str(tz)) for tz in pytz.all_timezones)
    vocabulary = vocabulary.SimpleVocabulary.from_items(
        *[(str(tz).lower(), str(tz).lower(), str(tz))
          for tz in pytz.all_timezones])

    def dumps(self, value):
        return super(TimezoneField, self).dumps(self.serialize(value))

    def loads(self, value):
        if not value.startswith('"'):
            value = '"{0}"'.format(value)

        value = super(TimezoneField, self).loads(value)
        return self.deserialize(value)

    def serialize(self, value):
        if value is null:
            return null

        return str(value).lower()

    def deserialize(self, value):
        if value is null or not value:
            return null

        try:
            v = str(value).lower()
            if v.startswith('gmt'):
                v = 'etc/%s' % v
            try:
                return pytz.timezone(v)
            except:
                return pytz.timezone(self._tzs[v])
        except:
            raise Invalid(self,
                _('"${val}" is not a timezone', mapping={'val': value}))
