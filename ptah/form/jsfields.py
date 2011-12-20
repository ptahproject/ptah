""" various fields """
import datetime

import ptah
from ptah import view, formatter
from ptah.form.interfaces import _, null, Invalid
from ptah.form.field import field
from ptah.form.fields import TextAreaField, TextField, DateTimeField


@field('tinymce')
class TinymceField(TextAreaField):
    """TinyMCE Text Area input widget. Field name is ``tinymce``.

    Extra params:

    :param width: Width of widget, default is ``400px``
    :param height: Height os widget, default is ``300px``
    :param theme: TinyMCE theme
    """

    klass = 'tinymce-widget'

    width = '400px'
    height = '300px'
    theme = "advanced"

    tmpl_input = "ptah.form:templates/fields/tinymce_input.pt"


@field('date')
class JSDateField(TextField):
    """Date input widget with JQuery Datepicker. Field name is ``date``."""

    klass = 'date-widget'
    value = ''

    tmpl_input = "ptah.form:templates/fields/jsdate-input.pt"

    def serialize(self, value):
        if value is null or value is None:
            return null

        if isinstance(value, datetime.datetime):
            value = value.date()

        if not isinstance(value, datetime.date):
            raise Invalid(self,
                          _('"${val}" is not a date object',
                            mapping={'val': value}))

        return value.strftime('%m/%d/%Y')

    def deserialize(self, value):
        if not value:
            return null
        try:
            return datetime.datetime.strptime(value, '%m/%d/%Y').date()
        except Exception as e:
            raise Invalid(
                self, _('Invalid date', mapping={'val': value, 'err': e}))


@field('datetime')
class JSDateTimeField(DateTimeField):
    """DateTime input widget with JQuery Datepicker.
    Field name is ``datetime``."""

    klass = 'datetime-widget'
    value = ''

    time_part = null
    date_part = null
    tzinfo = None

    tmpl_input = "ptah.form:templates/fields/jsdatetime-input.pt"

    def update(self, request):
        self.date_name = '%s.date' % self.name
        self.time_name = '%s.time' % self.name

        super(JSDateTimeField, self).update(request)

        self.date_part = self.params.get(self.date_name, null)
        self.time_part = self.params.get(self.time_name, null)

        if self.value:
            raw = self.value
            self.tzinfo = raw.tzinfo
            if self.date_part is null:
                self.date_part = raw.strftime('%m/%d/%Y')
            if self.time_part is null:
                FORMAT = ptah.get_settings(ptah.CFG_ID_FORMAT, request.registry)
                self.time_part = raw.strftime(FORMAT['time_short'])

        if self.date_part is null:
            self.date_part = ''
        if self.time_part is null:
            self.time_part = ''

    def extract(self, default=null):
        date = self.params.get(self.date_name, default)
        if date is default:
            return default

        if not date:
            return null

        time = self.params.get(self.time_name, default)
        if time is default:
            return default

        if not time:
            return null

        FORMAT = ptah.get_settings(ptah.CFG_ID_FORMAT, self.request.registry)
        format = '%s %s' % ('%m/%d/%Y', FORMAT['time_short'])
        try:
            dt = datetime.datetime.strptime('%s %s' % (date, time), format)
        except ValueError:
            return null

        return dt.replace(tzinfo=self.tzinfo).isoformat()
