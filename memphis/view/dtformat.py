""" date fomratters """
import pytz
import translationstring
from datetime import date, datetime, timedelta

from memphis import config
from memphis.config import colander
from memphis.config.colander import null
from memphis.view.compat import translate
from memphis.view.formatter import format

_ = translationstring.TranslationStringFactory('memphis.view')

_tzs = dict((str(tz).lower(), str(tz)) for tz in pytz.common_timezones)


class Timezone(colander.SchemaType):
    """ timezone """

    def serialize(self, node, appstruct):
        if appstruct is null:
            return null

        return str(appstruct)

    def deserialize(self, node, cstruct):
        try:
            v = str(cstruct)
            try:
                return pytz.timezone(v)
            except:
                return pytz.timezone(_tzs[v.lower()])
        except Exception, e:
            raise Invalid(
                node, _('${val} is not a timezone', mapping={'val':cstruct}))


FORMAT = config.registerSettings(
    'format',

    colander.SchemaNode(
        Timezone(),
        name = 'timezone',
        default = pytz.timezone('US/Pacific'),
        title = _('Timezone'),
        description = _('Site wide timezone.')),

    colander.SchemaNode(
        colander.Str(),
        name = 'date_short',
        default = u'%m/%d/%y',
        title = _(u'Date'),
        description = _(u'Date short format')),

    colander.SchemaNode(
        colander.Str(),
        name = 'date_medium',
        default = u'%b %d, %Y',
        title = _(u'Date'),
        description = _(u'Date medium format')),

    colander.SchemaNode(
        colander.Str(),
        name = 'date_long',
        default = u'%B %d, %Y',
        title = _(u'Date'),
        description = _(u'Date long format')),

    colander.SchemaNode(
        colander.Str(),
        name = 'date_full',
        default = u'%A, %B %d, %Y',
        title = _(u'Date'),
        description = _(u'Date full format')),

    colander.SchemaNode(
        colander.Str(),
        name = 'time_short',
        default = u'%I:%M %p',
        title = _(u'Time'),
        description = _(u'Time short format')),

    colander.SchemaNode(
        colander.Str(),
        name = 'time_medium',
        default = u'%I:%M:%S %p',
        title = _(u'Time'),
        description = _(u'Time medium format')),

    colander.SchemaNode(
        colander.Str(),
        name = 'time_long',
        default = u'%I:%M:%S %p %z',
        title = _(u'Time'),
        description = _(u'Time long format')),

    colander.SchemaNode(
        colander.Str(),
        name = 'time_full',
        default = u'%I:%M:%S %p %Z',
        title = _(u'Time'),
        description = _(u'Time full format')),

    title = 'Varios formats',
    )


def datetimeFormatter(value, tp='medium', request=None):
    """ datetime format """
    if not isinstance(value, datetime):
        return value

    tz = FORMAT.timezone
    if value.tzinfo is None:
        value = datetime(value.year, value.month, value.day, value.hour,
                         value.minute, value.second, value.microsecond, tz)

    value = value.astimezone(tz)
    format = '%s %s'%(FORMAT['date_%s'%tp], FORMAT['time_%s'%tp])
    return unicode(value.strftime(str(format)))


def timedeltaFormatter(value, type='short', request=None):
    """ timedelta formatter """
    if not isinstance(value, timedelta):
        return value

    if type == 'full':
        hours = value.seconds/3600
        hs = hours*3600
        mins = (value.seconds - hs)/60
        ms = mins*60
        secs = value.seconds - hs - ms
        frm = []
        if hours:
            frm.append(translate(
                    '${hours} hour(s)', mapping={'hours': hours}))
        if mins:
            frm.append(translate(
                    '${mins} min(s)', mapping={'mins': mins}))
        if secs:
            frm.append(translate(
                    '${secs} sec(s)', mapping={'secs': secs}))

        return ' '.join(frm)

    elif type == 'medium':
        return str(value)
    else:
        return str(value).split('.')[0]


format['datetime'] = datetimeFormatter
format['timedelta'] = timedeltaFormatter
