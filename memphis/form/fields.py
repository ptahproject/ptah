""" Basic fields """
from memphis import view
from memphis.form.directive import widget
from memphis.form.interfaces import _, null, required
from memphis.form import htmlwidget
from memphis.form.field import Field, SequenceField
from memphis.form.error import Invalid


class TextField(htmlwidget.HTMLTextInputWidget, Field):
    __doc__ = _(u'HTML Text input widget')

    widget('text', _(u'Text widget'))

    klass = u'text-widget'
    value = u''

    tmpl_input = view.template(
        "memphis.form:templates/fields/text_input.pt")
    tmpl_display = view.template(
        "memphis.form:templates/fields/text_display.pt")


class TextAreaField(htmlwidget.HTMLTextAreaWidget, Field):
    __doc__ = _(u'HTML Text Area input widget')

    widget('textarea', _(u'TextArea widget'))

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

    widget('file', _(u'File widget'))
    klass = u'input-file'

    tmpl_input = view.template(
        "memphis.form:templates/fields/file_input.pt")
    tmpl_display = view.template(
        "memphis.form:templates/fields/file_display.pt")

    def extract(self, params, value):
        if hasattr(value, 'file'):
            data = {}
            data['fp'] = value.file
            data['filename'] = value.filename
            data['mimetype'] = value.type
            data['size'] = value.length
            return data
        else:
            if self.missing is required:
                raise Invalid(self, _('Required'))

            return self.missing


class TinymceField(TextAreaField):
    __doc__ = _(u'TinyMCE Text Area input widget')

    widget('tinymce', _(u'TinyMCE widget'))

    klass = u'tinymce-widget'

    width = '400px'
    height = '300px'
    theme = "advanced"

    tmpl_input = view.template(
        "memphis.form:templates/fields/tinymce_input.pt")


class TextLinesField(TextAreaField):
    __doc__ = _('Text area based widget, each line is treated as '
                'sequence element.')

    widget('textlines', _('Text lines widget'))

    def extract(self, params, default = null):
        value = params.get(self.name, default)
        if value is not default:
            return value.split(u'\n')
        return value

    tmpl_input = view.template(
        "memphis.form:templates/fields/textlines_input.pt")
    tmpl_display = view.template(
        "memphis.form:templates/fields/textlines_display.pt")


class PasswordField(TextField):
    __doc__ = _('HTML Password input widget.')

    widget('password', _('Password Widget'))

    klass = u'password-widget'

    tmpl_input = view.template(
        "memphis.form:templates/fields/password_input.pt")
    tmpl_display = view.template(
        "memphis.form:templates/fields/password_display.pt")


class CheckBoxField(htmlwidget.HTMLInputWidget, SequenceField):
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

    def update(self):
        """See z3c.form.interfaces.IWidget."""
        super(CheckBoxWidget, self).update()

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


class DateField(htmlwidget.HTMLTextInputWidget, Field):
    __doc__ = _(u'Date input widget with JQuery Datepicker.')

    widget('date', 'Date widget')

    klass = u'date-widget'
    value = u''

    __fname__ = 'date'
    __title__ = _(u'Date widget')
    __description__ = _(u'Date input widget with JQuery Datepicker.')

    tmpl_input = view.template(
        "memphis.form:templates/fields/date_input.pt")
    tmpl_display = view.template(
        "memphis.form:templates/fields/date_display.pt")


class DatetimeField(htmlwidget.HTMLTextInputWidget, Field):
    __doc__ = _(u'DateTime input widget with JQuery Datepicker.')

    widget('datetime', 'DateTime widget')

    klass = u'datetime-widget'
    value = u''

    __fname__ = 'datetime'
    __title__ = _(u'DateTime widget')

    time_part = null
    date_part = null
    tzinfo = None

    tmpl_input = view.template(
        "memphis.form:templates/fields/datetime_input.pt")
    tmpl_display = view.template(
        "memphis.form:templates/fields/datetime_display.pt")

    def update(self):
        self.date_name = '%s.date'%self.name
        self.time_name = '%s.time'%self.name

        super(DatetimeWidget, self).update()

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


class RadioField(htmlwidget.HTMLInputWidget, SequenceField):
    __doc__ = _('HTML Radio input widget.')

    widget('radio', _('Radio widget'))

    klass = u'radio-widget'
    items = ()

    tmpl_input = view.template(
        "memphis.form:templates/fields/radio_input.pt")
    tmpl_display = view.template(
        "memphis.form:templates/fields/radio_display.pt")

    def isChecked(self, term):
        return term.token in self.value

    def update(self):
        super(RadioWidget, self).update()

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


class HorizontalRadioField(RadioField):
    __doc__ = _('HTML Radio input widget.')
    widget('radio-horizontal', _('Horizontal Radio widget'))

    tmpl_input = view.template(
        "memphis.form:templates/fields/radiohoriz_input.pt")


class SelectField(htmlwidget.HTMLSelectWidget, SequenceField):
    __doc__ = _('HTML Select input widget.')

    klass = u'select-widget'
    prompt = False

    widget('select', _('Select widget'))

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

    widget('multiselect', _('Multi select widget'))
