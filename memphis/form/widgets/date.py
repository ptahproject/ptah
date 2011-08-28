""" jquery date/datetime widget """
import colander, iso8601
from zope import interface
from datetime import datetime

from memphis import config, view
from memphis.view import formatter
from memphis.form import pagelets, Widget

from widget import HTMLTextInputWidget
from interfaces import _, IDateWidget, IDatetimeWidget


class DateWidget(HTMLTextInputWidget, Widget):
    __doc__ = _(u'Date input widget with JQuery Datepicker.')
    interface.implementsOnly(IDateWidget)
    config.adapts(colander.SchemaNode, colander.Date)

    klass = u'date-widget'
    value = u''

    __fname__ = 'date'
    __title__ = _(u'Date widget')
    __description__ = _(u'Date input widget with JQuery Datepicker.')


view.registerPagelet(
    'form-display', IDateWidget,
    template=view.template("memphis.form.widgets:date_display.pt"))

view.registerPagelet(
    'form-input', IDateWidget,
    template=view.template("memphis.form.widgets:date_input.pt"))


class DatetimeWidget(HTMLTextInputWidget, Widget):
    __doc__ = _(u'DateTime input widget with JQuery Datepicker.')
    interface.implementsOnly(IDatetimeWidget)
    config.adapts(colander.SchemaNode, colander.DateTime)

    klass = u'datetime-widget'
    value = u''

    __fname__ = 'datetime'
    __title__ = _(u'DateTime widget')

    time_part = colander.null
    date_part = colander.null
    tzinfo = None

    def __init__(self, node, typ):
        super(DatetimeWidget, self).__init__(node, typ)

        self.date_name = '%s.date'%node.name
        self.time_name = '%s.time'%node.name

    def update(self):
        super(DatetimeWidget, self).update()

        self.date_part = self.params.get(self.date_name, colander.null)
        self.time_part = self.params.get(self.time_name, colander.null)

        if self.value:
            try:
                raw = iso8601.parse_date(self.value)
            except:
                pass
            else:
                self.tzinfo = raw.tzinfo
                if self.date_part is colander.null:
                    self.date_part = raw.strftime('%m/%d/%Y')
                if self.time_part is colander.null:
                    self.time_part = raw.strftime(formatter.FORMAT.time_short)

        if self.date_part is colander.null:
            self.date_part = u''
        if self.time_part is colander.null:
            self.time_part = u''

    def extract(self, default=colander.null):
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


view.registerPagelet(
    'form-display', IDatetimeWidget,
    template=view.template("memphis.form.widgets:datetime_display.pt"))

view.registerPagelet(
    'form-input', IDatetimeWidget,
    template=view.template("memphis.form.widgets:datetime_input.pt"))
