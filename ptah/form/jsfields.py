""" various fields """
import datetime
from ptah import view, formatter

from interfaces import null
from field import field
from fields import TextAreaField, DateField, DateTimeField


class TinymceField(TextAreaField):
    __doc__ = u'TinyMCE Text Area input widget'

    field('tinymce')

    klass = u'tinymce-widget'

    width = '400px'
    height = '300px'
    theme = "advanced"

    tmpl_input = view.template(
        "ptah.form:templates/fields/tinymce_input.pt")


class JSDateField(DateField):
    __doc__ = u'Date input widget with JQuery Datepicker.'

    field('date')

    klass = u'date-widget'
    value = u''

    tmpl_input = view.template(
        "ptah.form:templates/fields/jsdate-input.pt")


class JSDateTimeField(DateTimeField):
    __doc__ = u'DateTime input widget with JQuery Datepicker.'

    field('datetime')

    klass = u'datetime-widget'
    value = u''

    time_part = null
    date_part = null
    tzinfo = None

    tmpl_input = view.template(
        "ptah.form:templates/fields/jsdatetime-input.pt")

    def update(self, request):
        self.date_name = '%s.date'%self.name
        self.time_name = '%s.time'%self.name

        super(JSDateTimeField, self).update(request)

        self.date_part = self.params.get(self.date_name, null)
        self.time_part = self.params.get(self.time_name, null)

        if self.value:
            raw = self.value
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
            return null

        time = self.params.get(self.time_name, default)
        if time is default:
            return default

        if not time:
            return null

        format = '%s %s'%(
            '%m/%d/%Y', formatter.FORMAT.time_short)
        try:
            dt = datetime.datetime.strptime('%s %s'%(date, time), format)
        except ValueError:
            return null

        return dt.replace(tzinfo=self.tzinfo).isoformat()
