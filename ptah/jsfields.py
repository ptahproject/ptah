""" various fields """
import ptah
import datetime
import pform
from pform.interfaces import _, null, Invalid
from pform.fields import TextAreaField, TextField, DateTimeField


@pform.field('ckeditor')
class CKEditorField(TextAreaField):
    """ CKEditor input widget. Field name is ``ckeditor``.

    Extra params:

    :param width: Width of widget, default is ``400px``
    :param height: Height os widget, default is ``300px``
    """

    klass = 'ckeditor-widget'

    width = '400px'
    height = '300px'

    tmpl_input = "ptah:ckeditor"


@pform.field('date')
class JSDateField(TextField):
    """Date input widget with JQuery Datepicker. Field name is ``date``."""

    klass = 'date-widget'
    value = ''

    tmpl_input = "ptah:jsdate"

    def to_form(self, value):
        if value is null or value is None:
            return null

        if isinstance(value, datetime.datetime):
            value = value.date()

        if not isinstance(value, datetime.date):
            raise Invalid(self,
                          _('"${val}" is not a date object',
                            mapping={'val': value}))

        return value.strftime('%m/%d/%Y')

    def to_field(self, value):
        if not value:
            return null
        try:
            return datetime.datetime.strptime(value, '%m/%d/%Y').date()
        except Exception as e:
            raise Invalid(
                self, _('Invalid date', mapping={'val': value, 'err': e}))


@pform.field('datetime')
class JSDateTimeField(DateTimeField):
    """DateTime input widget with JQuery Datepicker.
    Field name is ``datetime``."""

    klass = 'datetime-widget'
    value = ''

    time_part = null
    date_part = null
    tzinfo = None

    tmpl_input = "ptah:jsdatetime"

    def update(self):
        self.date_name = '%s.date' % self.name
        self.time_name = '%s.time' % self.name

        super(JSDateTimeField, self).update()

        self.date_part = self.params.get(self.date_name, null)
        self.time_part = self.params.get(self.time_name, null)

        if self.value:
            raw = self.value
            self.tzinfo = raw.tzinfo
            if self.date_part is null:
                self.date_part = raw.strftime('%m/%d/%Y')
            if self.time_part is null:
                FORMAT = ptah.get_settings(
                    ptah.CFG_ID_FORMAT, self.request.registry)
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

        #FORMAT = ptah.get_settings(ptah.CFG_ID_FORMAT, self.request.registry)
        try:
            dt = datetime.datetime.strptime(
                '%s %s' % (date, time), '%m/%d/%Y %H:%M')
        except ValueError:
            try:
                dt = datetime.datetime.strptime(
                    '%s %s' % (date, time), '%m/%d/%Y %I:%M %p')
            except ValueError:
                return null

        return dt.replace(tzinfo=self.tzinfo).isoformat()
