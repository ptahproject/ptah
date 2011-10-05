""" Basic fields """
import datetime, iso8601
from memphis import view
from memphis.view import formatter
from memphis.form import vocabulary
from memphis.form.field import field, Field, SequenceField
from memphis.form.interfaces import _, null, required, Invalid, ITerm


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

    def serialize(self, value):
        return value

    def deserialize(self, value):
        return value


class TextField(InputField):
    __doc__ = _(u'HTML Text input widget')

    field('text')

    klass = u'text-widget'
    value = u''

    tmpl_input = view.template(
        "memphis.form:templates/fields/text_input.pt")
    tmpl_display = view.template(
        "memphis.form:templates/fields/text_display.pt")


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
                self, _('"${val}" is not a number', mapping={'val':value}))


class IntegerField(Number, TextField):
    __doc__ = _(u'Integer input widget')

    field('int')

    klass = u'int-widget'
    value = 0

    num = int


class FloatField(Number, TextField):
    __doc__ = _(u'Float input widget')

    field('float')

    klass = u'float-widget'

    num = float


class Decimal(Number):
    __doc__ = _(u'Decimal input widget')

    field('decimal')

    klass = u'decimal-widget'

    def num(self, val):
        return decimal.Decimal(str(val))


class TextAreaField(TextField):
    __doc__ = _(u'HTML Text Area input widget')

    field('textarea')

    klass = u'textarea-widget'
    value = u''

    rows = 5
    cols = 40

    tmpl_input = view.template(
        "memphis.form:templates/fields/textarea_input.pt")
    tmpl_display = view.template(
        "memphis.form:templates/fields/textarea_display.pt")


class FileField(TextField):
    __doc__ = _(u'HTML File input widget')

    field('file')
    klass = u'input-file'

    tmpl_input = view.template(
        "memphis.form:templates/fields/file_input.pt")
    tmpl_display = view.template(
        "memphis.form:templates/fields/file_display.pt")

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


class TinymceField(TextAreaField):
    __doc__ = _(u'TinyMCE Text Area input widget')

    field('tinymce')

    klass = u'tinymce-widget'

    width = '400px'
    height = '300px'
    theme = "advanced"

    tmpl_input = view.template(
        "memphis.form:templates/fields/tinymce_input.pt")


class LinesField(TextAreaField):
    __doc__ = _('Text area based widget, each line is treated as '
                'sequence element.')

    field('lines')

    def serialize(self, value):
        return u'\n'.join(value)

    def extract(self, default = null):
        value = self.params.get(self.name, default)
        if value is not default:
            return value.split(u'\n')
        return value

    tmpl_input = view.template(
        "memphis.form:templates/fields/textlines_input.pt")
    tmpl_display = view.template(
        "memphis.form:templates/fields/textlines_display.pt")


class PasswordField(TextField):
    __doc__ = _('HTML Password input widget.')

    field('password')

    klass = u'password-widget'

    tmpl_input = view.template(
        "memphis.form:templates/fields/password_input.pt")
    tmpl_display = view.template(
        "memphis.form:templates/fields/password_display.pt")


class CheckBoxField(SequenceField):
    """Input type checkbox widget implementation."""

    klass = u'checkbox-widget'
    items = ()

    __fname__ = 'checkbox'
    __title__ = _('Checkbox widget')
    __description__ = _('HTML Checkbox input based widget.')

    tmpl_input = view.template(
        "memphis.form:templates/fields/checkbox_input.pt")
    tmpl_display = view.template(
        "memphis.form:templates/fields/checkbox_display.pt")

    def isChecked(self, term):
        return term.token in self.value

    def update(self, request):
        """See z3c.form.interfaces.IWidget."""
        super(CheckBoxWidget, self).update(request)

        self.items = []
        for count, term in enumerate(self.terms):
            checked = self.isChecked(term)
            id = '%s-%i' % (self.id, count)
            label = term.token
            if ITerm.providedBy(term):
                label = self.localizer.translate(term.title)
            self.items.append(
                {'id':id, 'name':self.name, 'value':term.token,
                 'label':label, 'checked':checked})


class SingleCheckBoxField(CheckBoxField):
    """Single Input type checkbox widget implementation."""

    klass = u'single-checkbox-widget'

    __fname__ = 'singlecheckbox'
    __title__ = _('Single checkbox')
    __description__ = _('Single checkbox widget.')

    def updateTerms(self):
        if self.terms is None:
            self.terms = vocabulary.Vocabulary()
            self.terms.terms = vocabulary.SimpleVocabulary(
                vocabulary.SimpleTerm('selected', 'selected', ''))
        return self.terms


class DateField(InputField):
    __doc__ = _(u'Simple date input field.')

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
            except Exception, e:
                raise Invalid(
                    self, _('Invalid date', mapping={'val': value, 'err': e}))

        return result


class JSDateField(DateField):
    __doc__ = _(u'Date input widget with JQuery Datepicker.')

    field('date')

    klass = u'date-widget'
    value = u''

    tmpl_input = view.template(
        "memphis.form:templates/fields/date_input.pt")
    tmpl_display = view.template(
        "memphis.form:templates/fields/date_display.pt")


class DateTimeField(InputField):

    default_tzinfo = iso8601.iso8601.Utc()

    def serialize(self, value):
        if value is null or value is None:
            return null

        if type(value) is datetime.date: # cant use isinstance; dt subs date
            value = datetime.datetime.combine(value, datetime.time())

        if not isinstance(value, datetime.datetime):
            raise Invalid(
                self, _('"${val}" is not a datetime object',
                        mapping={'val':value}))

        if value.tzinfo is None:
            value = value.replace(tzinfo=self.default_tzinfo)

        return value.isoformat()

    def deserialize(self, value):
        if not value:
            return null

        try:
            result = iso8601.parse_date(
                value, default_timezone=self.default_tzinfo)
        except (iso8601.ParseError, TypeError), e:
            try:
                year, month, day = map(int, value.split('-', 2))
                result = datetime.datetime(year, month, day,
                                           tzinfo=self.default_tzinfo)
            except Exception, e:
                raise Invalid(self, _('Invalid date',
                                      mapping={'val': value, 'err':e}))
        return result


class DatetimeField(DateTimeField):
    __doc__ = _(u'DateTime input widget with JQuery Datepicker.')

    field('datetime')

    klass = u'datetime-widget'
    value = u''

    time_part = null
    date_part = null
    tzinfo = None

    tmpl_input = view.template(
        "memphis.form:templates/fields/datetime_input.pt")
    tmpl_display = view.template(
        "memphis.form:templates/fields/datetime_display.pt")

    def update(self, request):
        self.date_name = '%s.date'%self.name
        self.time_name = '%s.time'%self.name

        super(DatetimeField, self).update(request)

        self.date_part = self.params.get(self.date_name, null)
        self.time_part = self.params.get(self.time_name, null)

        if self.value:
            try:
                raw = iso8601.parse_date(self.value)
            except:
                pass
            else:
                self.tzinfo = raw.tzinfo
                if self.date_part is null:
                    self.date_part = raw.strftime('%m/%d/%Y')
                if self.time_part is null:
                    self.time_part = raw.strftime(formatter.FORMAT.time_short)

        if self.date_part is null:
            self.date_part = u''
        if self.time_part is null:
            self.time_part = u''

    def extract(self, default=null):
        date = self.params.get(self.date_name, default)
        if date is default:
            return default

        if not date:
            return ''

        time = self.params.get(self.time_name, default)
        if time is default:
            return default

        if not time:
            return ''

        format = '%s %s'%(
            '%m/%d/%Y',
            formatter.FORMAT.time_short)
        try:
            dt = datetime.strptime('%s %s'%(date, time), format)
        except ValueError:
            return '--------'

        return dt.replace(tzinfo=self.tzinfo).isoformat()


class RadioField(SequenceField, InputField):
    __doc__ = _('HTML Radio input widget.')

    field('radio')

    klass = u'radio-widget'
    items = ()

    tmpl_input = view.template(
        "memphis.form:templates/fields/radio_input.pt")
    tmpl_display = view.template(
        "memphis.form:templates/fields/radio_display.pt")

    def isChecked(self, term):
        return term.token == self.value

    def update(self, request):
        super(RadioField, self).update(request)

        self.items = []
        for count, term in enumerate(self.terms):
            checked = self.isChecked(term)
            id = '%s-%i' % (self.id, count)
            label = term.token
            if ITerm.providedBy(term):
                label = self.localizer.translate(term.title)
            self.items.append(
                {'id':id, 'name':self.name, 'value':term.token,
                 'label':label, 'checked':checked})

    def extract(self, default=null):
        value = super(RadioField, self).extract(default)
        if value is not default:
            return value[0]
        return value


class HorizontalRadioField(RadioField):
    __doc__ = _('HTML Radio input widget.')

    field('radio-horizontal')

    tmpl_input = view.template(
        "memphis.form:templates/fields/radiohoriz_input.pt")


class BoolField(HorizontalRadioField):
    __doc__ = _('Boolean input widget.')

    field('bool')

    terms = vocabulary.SimpleVocabulary(
        vocabulary.SimpleTerm(True, 'true',  _('yes')),
        vocabulary.SimpleTerm(False, 'false',  _('no')))


class SelectField(SequenceField, InputField):
    __doc__ = _('HTML Select input widget.')

    klass = u'select-widget'
    prompt = False

    multiple = None
    size = 1

    field('select')

    noValueMessage = _('no value')
    promptMessage = _('select a value ...')

    tmpl_input = view.template(
        "memphis.form:templates/fields/select_input.pt",
        title="HTML Select: input template")
    tmpl_display = view.template(
        "memphis.form:templates/fields/select_display.pt",
        title="HTML Select: display template")

    def isSelected(self, term):
        return term.token in self.value

    @property
    def items(self):
        if self.terms is None:  # update() has not been called yet
            return ()
        items = []
        if (not self.required or self.prompt) and self.multiple is None:
            message = self.noValueMessage
            if self.prompt:
                message = self.promptMessage
            items.append({
                'id': self.id + '-novalue',
                'value': self.noValueToken,
                'content': message,
                'selected': self.value == []
                })

        for count, term in enumerate(self.terms):
            selected = self.isSelected(term)
            id = '%s-%i' % (self.id, count)
            content = term.token
            if ITerm.providedBy(term):
                content = self.localizer.translate(term.title)
            items.append(
                {'id':id, 'value':term.token, 'content':content,
                 'selected':selected})
        return items


class MultiSelectField(SelectField):
    __doc__ = _('HTML Multi Select input widget.')

    size = 5
    multiple = 'multiple'

    field('multiselect')
