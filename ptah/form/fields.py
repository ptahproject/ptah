""" Basic fields """
import pytz
import inspect
import datetime
import decimal
from pyramid.compat import NativeIO, text_type, PY3

from ptah.form import iso8601
from ptah.form import vocabulary
from ptah.form.field import InputField
from ptah.form.fieldset import Fieldset
from ptah.form.directives import field
from ptah.form.composite import CompositeField
from ptah.form.interfaces import _, null, Invalid, IVocabulary


def takes_one_arg(fn, name):
    try:
        argspec = inspect.getargspec(fn)

        args = argspec[0]
        if len(args) == 1 and name in args:
            return True

    except TypeError:
        pass

    return False


def voc_factory_mapper(factory):

    if takes_one_arg(factory, 'request'):
        def _wrapper_request(form):
            return factory(getattr(form, 'request', None))
        return _wrapper_request

    elif takes_one_arg(factory, 'context'):
        def _wrapper_context(form):
            return factory(getattr(form, 'context', None))
        return _wrapper_context

    elif takes_one_arg(factory, 'content'):
        def _wrapper_content(form):
            return factory(getattr(form, 'content', None))
        return _wrapper_content

    else:
        def _wrapper(form):
            return factory(form)
        return _wrapper


class VocabularyField(InputField):

    vocabulary = None
    voc_factory = None

    no_value_token = '--NOVALUE--'

    def __init__(self, *args, **kw):
        super(VocabularyField, self).__init__(*args, **kw)

        if self.voc_factory is None and self.vocabulary is None:
            raise ValueError("Vocabulary or vocabulary factory is required.")

        if self.voc_factory is not None and self.vocabulary is not None:
            raise ValueError("Vocabulary and vocabulary factory are defined.")

        # convert vocabulary
        voc = self.vocabulary
        if (voc is not None and not IVocabulary.providedBy(voc)):
            self.vocabulary = vocabulary.Vocabulary(*voc)

        if self.voc_factory is not None:
            self.voc_factory = voc_factory_mapper(self.voc_factory)

    def bind(self, request, prefix, value, params, context=None):
        clone = super(VocabularyField, self).bind(
            request, prefix, value, params, context)

        if clone.vocabulary is None:
            clone.vocabulary = self.voc_factory(context)

        return clone

    def is_checked(self, term):
        raise NotImplementedError()

    def update_items(self):
        self.items = []

        for count, term in enumerate(self.vocabulary):
            label = term.title if term.title is not None else term.token

            self.items.append(
                {'id': '%s-%i' % (self.id, count), 'name': self.name,
                 'value': term.token, 'label': label,
                 'description': term.description,
                 'checked': self.is_checked(term)})


class BaseChoiceField(VocabularyField):
    """ base choice field """

    error_msg = _('"${val}" is not in vocabulary')

    def to_form(self, value):
        try:
            return self.vocabulary.get_term(value).token
        except LookupError:
            raise Invalid(self.error_msg, self, {'val': value})

    def to_field(self, value):
        if not value:
            return null

        try:
            return self.vocabulary.get_term_bytoken(value).value
        except LookupError:
            raise Invalid(self.error_msg, self, {'val': value})

    def is_checked(self, term):
        return 'checked' if term.token == self.form_value else None

    def update(self):
        super(BaseChoiceField, self).update()

        self.update_items()

    def extract(self):
        value = super(BaseChoiceField, self).extract()

        if not value or value == self.no_value_token:
            return null
        return value


class BaseMultiChoiceField(VocabularyField):
    """ multi choice field """

    missing = []
    error_msg = _('"${val}" is not in vocabulary')

    def to_form(self, value):
        val = value
        try:
            res = []
            for val in value:
                res.append(self.vocabulary.get_term(val).token)
            return res
        except:
            raise Invalid(self.error_msg, self, {'val': val})

    def to_field(self, value):
        if not value:
            return null

        val = value
        try:
            res = []
            for val in value:
                res.append(self.vocabulary.get_term_bytoken(val).value)
            return res
        except:
            raise Invalid(self.error_msg, self, {'val': val})

    def extract(self):
        if self.name not in self.params:
            return null

        value = []
        tokens = self.params.getall(self.name)
        for token in tokens:
            if token == self.no_value_token:
                continue

            value.append(token)

        return value

    def is_checked(self, term):
        return 'checked' if term.token in self.form_value else None

    def update(self):
        super(BaseMultiChoiceField, self).update()

        if self.form_value in (null, None):
            self.form_value = []

        self.update_items()


@field('text')
class TextField(InputField):
    """HTML Text input widget. Field name is ``text``."""

    klass = 'form-control text-widget'
    value = ''
    missing = ''


class Number(object):

    error_msg = _('"${val}" is not a number')

    def to_form(self, value):
        try:
            return str(self.typ(value))
        except Exception:
            raise Invalid(self.error_msg, self)

    def to_field(self, value):
        if not value:
            return null

        try:
            return self.typ(value)
        except Exception:
            raise Invalid(self.error_msg, self, mapping={'val': value})


@field('int')
class IntegerField(Number, TextField):
    """Integer input widget. Field name is ``int``."""

    typ = int
    value = 0
    klass = 'form-control int-widget'


@field('float')
class FloatField(Number, TextField):
    """Float input widget. Field name is ``float``."""

    typ = float
    klass = 'form-control float-widget'


@field('decimal')
class DecimalField(Number, TextField):
    """Decimal input widget. Field name is ``decimal``."""

    typ = decimal.Decimal
    klass = 'form-control decimal-widget'


@field('textarea')
class TextAreaField(TextField):
    """HTML Text Area input widget. Field name is ``textarea``."""

    klass = 'form-control textarea-widget'
    html_attrs = TextField.html_attrs + ('rows', 'cols')

    rows = 5
    cols = 40
    value = ''
    default = ''

    tmpl_input = 'form:textarea'


@field('file')
class FileField(InputField):
    """HTML File input widget. Field name is ``file``."""

    klass = 'input-file'
    html_type = 'file'

    max_size = 0
    allowed_types = ()

    error_max_size = "Maximum file size exceeded."
    error_unknown_type = "Unknown file type."

    tmpl_input = 'form:input-file'

    def validate(self, value):
        if value is null and self.form_value:
            value = self.form_value

        super(FileField, self).validate(value)

        if value is null:
            return

        if self.max_size:
            value['fp'].seek(0, 2)
            size = value['fp'].tell()
            value['fp'].seek(0)

            if size > self.max_size:
                raise Invalid(self.error_max_size, self)

        if self.allowed_types and value['mimetype'] not in self.allowed_types:
            raise Invalid(self.error_unknown_type, self)

    def extract(self):
        value = self.params.get(self.name, null)

        if hasattr(value, 'file'):
            value.file.seek(0)
            return {
                'fp': value.file,
                'filename': value.filename,
                'mimetype': value.type,
                'size': value.length}
        elif value:
            if not PY3 and isinstance(value, text_type):
                value = value.encode('latin1')

            fp = NativeIO(value)
            fp.filename = self.params.get('%s-filename'%self.name, '')
            return {
                'fp': fp,
                'filename': self.params.get('%s-filename'%self.name, ''),
                'mimetype': self.params.get('%s-mimetype'%self.name, ''),
                'size': len(value)}

        return null


@field('lines')
class LinesField(TextAreaField):
    """Text area based widget, each line is treated as sequence element.
    Field name is ``lines``."""

    klass = 'form-control textlines-widget'
    missing = []

    error_msg = _('"${val}" is not a list')

    def to_form(self, value):
        try:
            return '\n'.join(value)
        except Exception:
            raise Invalid(self.error_msg, self, {'val': value})

    def to_field(self, value):
        if not value:
            return null

        try:
            return list(filter(None, [s.strip() for s in value.split('\n')]))
        except Exception:
            raise Invalid(self.error_msg, self, {'val': value})


@field('password')
class PasswordField(TextField):
    """HTML Password input widget. Field name is ``password``."""

    klass = 'form-control password-widget'
    html_type = 'password'


@field('multichoice')
class MultiChoiceField(BaseMultiChoiceField):
    """HTML Checkboxs input based widget. Field name is ``multichoice``."""

    klass = 'multichoice-widget'
    html_type = 'checkbox'
    tmpl_input = 'form:multichoice'


class DateField(TextField):
    """Simple date input field."""
    missing = None

    error_msg = _('"${val}" is not a date object')
    error_invalid_date = _('Invalid date')

    def to_form(self, value):
        if value is null:
            return null

        if isinstance(value, datetime.datetime):
            value = value.date()

        if not isinstance(value, datetime.date):
            raise Invalid(self.error_msg, self, {'val': value})

        return value.isoformat()

    def to_field(self, value):
        if not value:
            return null

        try:
            result = iso8601.parse_date(value)
            result = result.date()
        except (iso8601.ParseError, TypeError):
            try:
                year, month, day = map(int, value.split('-', 2))
                result = datetime.date(year, month, day)
            except Exception:
                raise Invalid(self.error_invalid_date, self)

        return result


class DateTimeField(TextField):

    default_tzinfo = iso8601.Utc()
    missing = None

    error_msg = _('"${val}" is not a datetime object')
    error_invalid_date = _('Invalid date')

    def to_form(self, value):
        if value is null or value is None or not value:
            return null

        if type(value) is datetime.date:  # cannot use isinstance; dt subs date
            value = datetime.datetime.combine(value, datetime.time())

        if not isinstance(value, datetime.datetime):
            raise Invalid(self.error_msg, self, {'val': value})

        if value.tzinfo is None:
            value = value.replace(tzinfo=self.default_tzinfo)

        return value.isoformat()

    def to_field(self, value):
        if not value:
            return null

        try:
            result = iso8601.parse_date(
                value, default_timezone=self.default_tzinfo)
        except (iso8601.ParseError, TypeError):
            try:
                year, month, day = map(int, value.split('-', 2))
                result = datetime.datetime(year, month, day,
                                           tzinfo=self.default_tzinfo)
            except Exception:
                raise Invalid(self.error_invalid_date, self)

        return result


@field('radio')
class RadioField(BaseChoiceField):
    """HTML Radio input widget. Field name is ``radio``."""

    klass = 'radio-widget'
    inline = False
    html_type = 'radio'
    html_attrs = BaseChoiceField.html_attrs + ('checked',)
    tmpl_input = 'form:radio'


@field('bool')
class BoolField(RadioField):
    """Boolean input widget. Field name is ``bool``."""

    vocabulary = vocabulary.Vocabulary(
        (True, 'true',  'yes'),
        (False, 'false',  'no'))

    inline = True


@field('choice')
class ChoiceField(BaseChoiceField):
    """HTML Select input widget. Field name is ``choice``."""

    size = 1
    klass = 'form-control select-widget'
    multiple = None
    prompt_message = _('select a value ...')

    tmpl_input = 'form:select'

    def update_items(self):
        super(ChoiceField, self).update_items()

        if not self.required:
            self.items.insert(0, {
                'id': self.id + '-novalue',
                'name': self.name,
                'value': self.no_value_token,
                'label': self.prompt_message,
                'checked': 'checked' if self.form_value is null else None,
                'description': '',
            })


@field('multiselect')
class MultiSelectField(BaseMultiChoiceField):
    """HTML Multi Select input widget. Field name is ``multiselect``.

    Extra params:

    :param size: Size of multiselect field, default is ``5``
    """

    size = 5
    html_attrs = BaseMultiChoiceField.html_attrs + ('multiple',)
    klass = 'form-control select-widget'
    multiple = 'multiple'
    tmpl_input = 'form:select'

    def update_items(self):
        super(MultiSelectField, self).update_items()

        if not self.required:
            self.items.insert(0, {
                'id': self.id + '-novalue',
                'name': self.name,
                'value': self.no_value_token,
                'label': self.prompt_message,
                'checked': 'checked' if self.form_value is null else None,
                'description': '',
            })


@field('timezone')
class TimezoneField(ChoiceField):
    """ Timezone field. Field name is ``timezone``."""

    error_msg = _('Invalid timezone "${val}"')

    _tzs = dict((str(tz).lower(), str(tz)) for tz in pytz.all_timezones)
    vocabulary = vocabulary.Vocabulary(
        *[(str(tz).lower(), str(tz).lower(), str(tz))
          for tz in pytz.all_timezones])

    def to_form(self, value):
        if value is null:
            return null

        return str(value).lower()

    def to_field(self, value):
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
            raise Invalid(self.error_msg, self, {'val': value})


class OptionsField(CompositeField):
    """ Options field

    ``key``: Name of group key name

    ``defaults``: Build defaults for unselected groups

    ``extract_all``: Extract values for all groups

    """

    key = ''
    defaults = False
    extract_all = False
    tmpl_input = 'form:options'

    def __init__(self, *args, **kw):
        super(OptionsField, self).__init__(*args, **kw)

        voc = vocabulary.Vocabulary(
            *[vocabulary.Term(fname, fname, field.title)
              for fname, field in self.fields.items()])

        if not self.key:
            self.key = self.name

        self.fields = Fieldset(
            RadioField(
                self.key,
                missing = voc[0].value,
                default = voc[0].value,
                required = False,
                vocabulary = voc)) + self.fields

    def to_field(self, value):
        value = super(OptionsField, self).to_field(value)

        if self.defaults:
            for name, f in self.fields.items():
                if name not in value:
                    value[name] = (f.default
                                   if f.default is not null else f.missing)

        return value

    def validate(self, value):
        key = value.get(self.key)

        if key not in self.fields:
            key = self.fields[self.key].default

        super(OptionsField, self).validate(
            {key: value.get(key, self.fields[key].missing)})

    def extract(self):
        value = super(OptionsField, self).extract()

        if not self.extract_all:
            opotion = value[self.key]
            if opotion in value:
                return {self.key: opotion, opotion: value[opotion]}
            else:
                return {}

        return value
