""" formatters """
import pytz
import translationstring
from datetime import datetime, timedelta
from pyramid.i18n import get_localizer
from pyramid.compat import text_type
from pyramid.threadlocal import get_current_request

import ptah
from ptah import config

_ = translationstring.TranslationStringFactory('ptah')

ID_FORMATTER = 'ptah:formatter'


def formatter(name):
    info = config.DirectiveInfo()

    def wrapper(func):
        discr = (ID_FORMATTER, name)

        intr = config.Introspectable(ID_FORMATTER, discr, name, ID_FORMATTER)

        intr['name'] = name
        intr['callable'] = func
        intr['description'] = func.__doc__
        intr['codeinfo'] = info.codeinfo

        info.attach(
            config.Action(
                lambda config, name, func:
                    config.get_cfg_storage(ID_FORMATTER).update({name: func}),
                (name, func), discriminator=discr, introspectables=(intr,))
            )
        return func

    return wrapper


class FormatImpl(dict):

    def __getattr__(self, name):
        try:
            return config.get_cfg_storage(ID_FORMATTER)[name]
        except KeyError:
            raise AttributeError(name)

format = FormatImpl()


@formatter('datetime')
def datetime_formatter(value, tp='medium', request=None):
    """DateTime formatter

    Short::

      >> dt = datetime(2011, 2, 6, 10, 35, 45, 80, pytz.UTC)

      >> ptah.format.datetime(dt, 'short')
      '02/06/11 04:35 AM'


    Medium::

      >> ptah.format.datetime(dt, 'medium')
      'Feb 06, 2011 04:35 AM'

    Long::

      >> ptah.format.datetime(dt, 'long')
      'February 06, 2011 04:35 AM -0600'

    Full::

      >> ptah.format.datetime(dt, 'full')
      'Sunday, February 06, 2011 04:35:45 AM CST'

    """
    if not isinstance(value, datetime):
        return value

    FORMAT = ptah.get_settings('format', request)

    tz = FORMAT['timezone']
    if value.tzinfo is None:
        value = datetime(value.year, value.month, value.day, value.hour,
                         value.minute, value.second, value.microsecond,
                         pytz.utc)

    value = value.astimezone(tz)

    format = '%s %s' % (FORMAT['date_%s' % tp], FORMAT['time_%s' % tp])
    return text_type(value.strftime(str(format)))


@formatter('timedelta')
def timedelta_formatter(value, type='short', request=None):
    """Timedelta formatter

    Full format::

      >> td = timedelta(hours=10, minutes=5, seconds=45)
      >> ptah.format.timedelta(td, 'full')
      '10 hour(s) 5 min(s) 45 sec(s)'

    Seconds::

      >> ptah.format.timedelta(td, 'seconds')
      '36345.0000'


    Default::

      >> ptah.format.timedelta(td)
      '10:05:45'

    """
    if not isinstance(value, timedelta):
        return value

    if request is None:
        request = get_current_request()

    if type == 'full':
        hours = value.seconds // 3600
        hs = hours * 3600
        mins = (value.seconds - hs) // 60
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
    'k': (1024.0, 'KB'),
    'm': (1024.0*1024.0, 'MB'),
    'g': (1024.0*1024.0*1024.0, 'GB'),
}


@formatter('size')
def size_formatter(value, type='k', request=None):
    """Size formatter

    bytes::

        >> v = 1024
        >> ptah.format.size(v, 'b')
        '1024 B'

    kylobytes::

        >> ptah.format.size(v, 'k')
        '1.00 KB'

    megabytes::

        >> ptah.format.size(1024*768, 'm')
        '0.75 MB'

        >> ptah.format.size(1024*768*768, 'm')
        '576.00 MB'

    terabytes::

        >> ptah.format.size(1024*768*768, 'g')
        '0.56 GB'

    """
    if not isinstance(value, (int, float)):
        return value

    f, t = _size_types.get(type, (1024.0, 'KB'))

    if t == 'B':
        return '%.0f %s' % (value / f, t)

    return '%.2f %s' % (value / f, t)
