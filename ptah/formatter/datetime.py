""" date/time formatters """
import pytz
from datetime import (
    date,
    datetime,
    time,
    timedelta
)
from babel.core import default_locale
from babel.dates import (
    format_date,
    format_datetime,
    format_time,
    get_timezone
)
from pyramid.compat import text_type


def date_formatter(request, value, format='medium', locale_name=None):
    """Date formatter
    """
    if not isinstance(value, datetime) and not isinstance(value, date):
        return value

    if not locale_name:
        locale_name = request.locale_name

    return text_type(format_date(value, format, locale_name))


def time_formatter(request, value, format='medium',
                   tzname=None, locale_name=None):
    """Time formatters
    """
    if not isinstance(value, datetime) and not isinstance(value, time):
        return value
    tzinfo = None

    if tzname:
        tzinfo = get_timezone(tzname)

    if not tzinfo:
        settings = request.registry.settings
        tzinfo = get_timezone(settings['ptah.timezone'])

    if not locale_name:
        locale_name = request.locale_name

    return text_type(format_time(value, format, tzinfo, locale_name))


def datetime_formatter(request, value, format='medium',
                       tzname=None, locale_name=None):
    """DateTime formatter

    Short::

      >> dt = datetime(2011, 2, 6, 10, 35, 45, 80, pytz.UTC)

      >> request.fmt.datetime(dt, 'short')
      '02/06/11 04:35 AM'


    Medium::

      >> request.fmt.datetime(dt, 'medium')
      'Feb 06, 2011 04:35 AM'

    Long::

      >> request.fmt.datetime(dt, 'long')
      'February 06, 2011 04:35 AM -0600'

    Full::

      >> request.fmt.datetime(dt, 'full')
      'Sunday, February 06, 2011 04:35:45 AM CST'

    """
    if not isinstance(value, datetime):
        return value

    tzinfo = None

    if tzname:
        tzinfo = get_timezone(tzname)

    if not tzinfo:
        settings = request.registry.settings
        tzinfo = get_timezone(settings['ptah.timezone'])

    if not locale_name:
        locale_name = request.locale_name

    return text_type(format_datetime(value, format, tzinfo, locale_name))


def timedelta_formatter(request, value, type='short'):
    """Timedelta formatter

    Full format::

      >> td = timedelta(hours=10, minutes=5, seconds=45)
      >> request.fmt.timedelta(td, 'full')
      '10 hour(s) 5 min(s) 45 sec(s)'

    Seconds::

      >> request.fmt.timedelta(td, 'seconds')
      '36345.0000'


    Default::

      >> request.fmt.timedelta(td)
      '10:05:45'

    """
    if not isinstance(value, timedelta):
        return value

    if type == 'full':
        hours = value.seconds // 3600
        hs = hours * 3600
        mins = (value.seconds - hs) // 60
        ms = mins * 60
        secs = value.seconds - hs - ms
        frm = []
        translate = request.localizer.translate

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
