""" various fields """
import datetime
from memphis import form, view
from memphis.view import formatter


class JSDateField(form.DateField):
    __doc__ = u'Date input widget with JQuery Datepicker.'

    form.field('date')

    klass = u'date-widget'
    value = u''

    tmpl_input = view.template(
        "ptah_app:templates/date-input.pt")


class JSDateTimeField(form.DateTimeField):
    __doc__ = u'DateTime input widget with JQuery Datepicker.'

    form.field('datetime')

    klass = u'datetime-widget'
    value = u''

    time_part = form.null
    date_part = form.null
    tzinfo = None

    tmpl_input = view.template(
        "ptah_app:templates/datetime-input.pt")

    def update(self, request):
        self.date_name = '%s.date'%self.name
        self.time_name = '%s.time'%self.name

        super(JSDateTimeField, self).update(request)

        self.date_part = self.params.get(self.date_name, form.null)
        self.time_part = self.params.get(self.time_name, form.null)

        if self.content:
            raw = self.content
            self.tzinfo = raw.tzinfo
            if self.date_part is form.null:
                self.date_part = raw.strftime('%m/%d/%Y')
            if self.time_part is form.null:
                self.time_part = raw.strftime(formatter.FORMAT.time_short)

        if self.date_part is form.null:
            self.date_part = u''
        if self.time_part is form.null:
            self.time_part = u''

    def extract(self, default=form.null):
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


@form.fieldpreview(JSDateField)
def jsdatePreview(request):
    field = JSDateField(
        'JSDateField',
        title = 'jQuery Date field',
        description = 'jQuery Date field preview description',
        default = datetime.date.today())

    widget = field.bind('preview.', form.null, {})
    widget.update(request)
    return widget.snippet('form-widget', widget)


@form.fieldpreview(JSDateTimeField)
def jsdatetimePreview(request):
    field = JSDateTimeField(
        'JSDateTimeField',
        title = 'jQuery DateTime field',
        description = 'jQuery DateTime field preview description')

    widget = field.bind('preview.', datetime.datetime.now(), {})
    widget.update(request)
    return widget.snippet('form-widget', widget)
