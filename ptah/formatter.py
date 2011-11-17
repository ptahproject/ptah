""" formatters """
import pytz
import colander
import translationstring
from datetime import datetime, timedelta
from pyramid.i18n import get_localizer
from pyramid.threadlocal import get_current_request

from ptah import config

_ = translationstring.TranslationStringFactory('ptah')


class FormatImpl(dict):

    def __setitem__(self, name, formatter):
        if name in self:
            raise ValueError('Formatter "%s" already registered.' % name)

        super(FormatImpl, self).__setitem__(name, formatter)

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)


format = FormatImpl()


_tzs = dict((str(tz).lower(), str(tz)) for tz in pytz.all_timezones)


class Timezone(colander.SchemaType):
    """ timezone schema type """

    def serialize(self, node, appstruct):
        if appstruct is colander.null:
            return colander.null

        return str(appstruct)

    def deserialize(self, node, cstruct):
        if cstruct is colander.null or not cstruct:
            return colander.null

        try:
            v = str(cstruct)
            if v.startswith('GMT'):
                v = 'Etc/%s' % v
            try:
                return pytz.timezone(v)
            except:
                return pytz.timezone(_tzs[v.lower()])
        except:
            raise colander.Invalid(node,
                _('"${val}" is not a timezone', mapping={'val': cstruct}))


FORMAT = config.register_settings(
    'format',

    config.SchemaNode(
        Timezone(),
        name = 'timezone',
        default = pytz.timezone('US/Central'),
        title = _('Timezone'),
        description = _('Site wide timezone.')),

    config.SchemaNode(
        colander.Str(),
        name = 'date_short',
        default = u'%m/%d/%y',
        title = _(u'Date'),
        description = _(u'Date short format')),

    config.SchemaNode(
        colander.Str(),
        name = 'date_medium',
        default = u'%b %d, %Y',
        title = _(u'Date'),
        description = _(u'Date medium format')),

    config.SchemaNode(
        colander.Str(),
        name = 'date_long',
        default = u'%B %d, %Y',
        title = _(u'Date'),
        description = _(u'Date long format')),

    config.SchemaNode(
        colander.Str(),
        name = 'date_full',
        default = u'%A, %B %d, %Y',
        title = _(u'Date'),
        description = _(u'Date full format')),

    config.SchemaNode(
        colander.Str(),
        name = 'time_short',
        default = u'%I:%M %p',
        title = _(u'Time'),
        description = _(u'Time short format')),

    config.SchemaNode(
        colander.Str(),
        name = 'time_medium',
        default = u'%I:%M %p',
        title = _(u'Time'),
        description = _(u'Time medium format')),

    config.SchemaNode(
        colander.Str(),
        name = 'time_long',
        default = u'%I:%M %p %z',
        title = _(u'Time'),
        description = _(u'Time long format')),

    config.SchemaNode(
        colander.Str(),
        name = 'time_full',
        default = u'%I:%M:%S %p %Z',
        title = _(u'Time'),
        description = _(u'Time full format')),

    title = 'Site formats',
    )


def datetimeFormatter(value, tp='medium', request=None):
    """ datetime format """
    if not isinstance(value, datetime):
        return value

    tz = FORMAT.timezone
    if value.tzinfo is None:
        value = datetime(value.year, value.month, value.day, value.hour,
                         value.minute, value.second, value.microsecond,
                         pytz.utc)

    value = value.astimezone(tz)

    format = '%s %s' % (FORMAT['date_%s' % tp], FORMAT['time_%s' % tp])
    return unicode(value.strftime(str(format)))


def timedeltaFormatter(value, type='short', request=None):
    """ timedelta formatter """
    if not isinstance(value, timedelta):
        return value

    if request is None:
        request = get_current_request()

    if type == 'full':
        hours = value.seconds / 3600
        hs = hours * 3600
        mins = (value.seconds - hs) / 60
        ms = mins * 60
        secs = value.seconds - hs - ms
        frm = []
        translate = get_localizer(request).translate

        if hours:
            frm.append(translate(
                    '${hours} hour(s)', 'ptah.view', {'hours': hours}))
        if mins:
            frm.append(translate(
                    '${mins} min(s)', 'ptah.view', {'mins': mins}))
        if secs:
            frm.append(translate(
                    '${secs} sec(s)', 'ptah.view', {'secs': secs}))

        return ' '.join(frm)

    elif type == 'medium':
        return str(value)
    elif type == 'seconds':
        s = value.seconds + value.microseconds / 1000000.0
        return '%2.4f' % s
    else:
        return str(value).split('.')[0]


_size_types = {
    'b': (1.0, 'B'),
    'k': (1024.0, 'Kb'),
    'm': (1048576.0, 'Mb'),
}


def sizeFormatter(value, type='k', request=None):
    """ size formatter """
    if not isinstance(value, (int, float)):
        return value

    f, t = _size_types.get(type, (1024.0, 'Kb'))

    if t == 'B':
        return '%.0f %s' % (value / f, t)

    return '%.2f %s' % (value / f, t)


format['datetime'] = datetimeFormatter
format['timedelta'] = timedeltaFormatter
format['size'] = sizeFormatter
