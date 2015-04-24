# ptah.formatter
from ptah.formatter.config import (
    add_formatter,
    formatters,
)
from ptah.formatter.datetime import (
    date_formatter,
    datetime_formatter,
    time_formatter,
    timedelta_formatter,
)
from ptah.formatter.size import size_formatter


def includeme(config):
    settings = config.get_settings()
    settings['ptah.timezone'] = settings.get('ptah.timezone', 'UTC')

    config.add_directive('add_formatter', add_formatter)
    config.add_request_method(formatters, 'fmt', True, True)

    config.add_formatter('date', date_formatter)
    config.add_formatter('time', time_formatter)
    config.add_formatter('datetime', datetime_formatter)
    config.add_formatter('timedelta', timedelta_formatter)
    config.add_formatter('size', size_formatter)
