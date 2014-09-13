""" formatter tests """
import pytz
from datetime import datetime, timedelta

import ptah
from ptah.testing import PtahTestCase


class TestFormatter(PtahTestCase):

    def test_date_formatter(self):
        format = self.request.fmt

        # format only datetime
        self.assertEqual(format.date('text string'), 'text string')

        dt = datetime(2011, 2, 6, 10, 35, 45, 80)
        self.assertEqual(format.date(dt, 'short'),
                         '2/6/11')
        self.assertEqual(format.date(dt, 'medium'),
                         'Feb 6, 2011')
        self.assertEqual(format.date(dt, 'long'),
                         'February 6, 2011')
        self.assertEqual(format.date(dt, 'full'),
                         'Sunday, February 6, 2011')

    def test_date_formatter_locale(self):
        format = self.request.fmt

        dt = datetime(2011, 2, 6, 10, 35, 45, 80)
        self.assertEqual(format.date(dt, 'full', 'es'),
                         'domingo, 6 de febrero de 2011')

    def test_time_formatter(self):
        format = self.request.fmt

        # format only datetime
        self.assertEqual(format.time('text string'), 'text string')

        dt = datetime(2011, 2, 6, 10, 35, 45, 80, pytz.UTC)
        self.assertEqual(format.time(dt, 'short'),
                         '10:35 AM')
        self.assertEqual(format.time(dt, 'medium'),
                         '10:35:45 AM')
        self.assertEqual(format.time(dt, 'long'),
                         '10:35:45 AM +0000')
        self.assertEqual(format.time(dt, 'full'),
                         '10:35:45 AM GMT+00:00')

    def test_time_formatter_timezone(self):
        format = self.request.fmt

        dt = datetime(2011, 2, 6, 10, 35, 45, 80, pytz.UTC)
        self.assertEqual(format.time(dt, 'long', 'US/Central'),
                         '4:35:45 AM CST')

    def test_time_formatter_locale(self):
        format = self.request.fmt

        dt = datetime(2011, 2, 6, 10, 35, 45, 80, pytz.UTC)
        self.assertEqual(format.time(dt, 'full', locale_name='es'),
                         '10:35:45 GMT+00:00')

    def test_datetime_formatter(self):
        format = self.request.fmt

        # format only datetime
        self.assertEqual(format.datetime('text string'), 'text string')

        dt = datetime(2011, 2, 6, 10, 35, 45, 80, pytz.UTC)
        self.assertEqual(format.datetime(dt, 'short'),
                         '2/6/11, 10:35 AM')
        self.assertEqual(format.datetime(dt, 'medium'),
                         'Feb 6, 2011, 10:35:45 AM')
        self.assertEqual(format.datetime(dt, 'long'),
                         'February 6, 2011 at 10:35:45 AM +0000')
        self.assertEqual(format.datetime(dt, 'full'),
                         'Sunday, February 6, 2011 at 10:35:45 AM GMT+00:00')

    def test_datetime_formatter_locale(self):
        format = self.request.fmt

        dt = datetime(2011, 2, 6, 10, 35, 45, 80, pytz.UTC)
        self.assertEqual(format.datetime(dt, 'long', locale_name='es'),
                         '6 de febrero de 2011 10:35:45 +0000')

    def test_datetime_formatter_timezone(self):
        format = self.request.fmt

        dt = datetime(2011, 2, 6, 10, 35, 45, 80, pytz.UTC)
        self.assertEqual(format.datetime(dt, 'long', 'US/Central'),
                         'February 6, 2011 at 4:35:45 AM CST')

    def test_timedelta_formatter(self):
        format = self.request.fmt

        # format only timedelta
        self.assertEqual(format.timedelta('text string'), 'text string')

        # full format
        td = timedelta(hours=10, minutes=5, seconds=45)

        self.assertEqual(format.timedelta(td, 'full'),
                         '10 hour(s) 5 min(s) 45 sec(s)')

        # medium format
        self.assertEqual(format.timedelta(td, 'medium'),
                         '10:05:45')

        # seconds format
        self.assertEqual(format.timedelta(td, 'seconds'),
                         '36345.0000')

        # default format
        self.assertEqual(format.timedelta(td), '10:05:45')

    def test_size_formatter(self):
        format = self.request.fmt

        # format only timedelta
        self.assertEqual(format.size('text string'), 'text string')

        v = 1024
        self.assertEqual(format.size(v, 'b'), '1024 B')

        self.assertEqual(format.size(v, 'k'), '1.00 KB')

        self.assertEqual(format.size(1024*768, 'm'), '0.75 MB')
        self.assertEqual(format.size(1024*768*768, 'm'), '576.00 MB')

        self.assertEqual(format.size(1024*768*768, 'g'), '0.56 GB')
