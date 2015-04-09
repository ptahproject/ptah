import pytz
from datetime import datetime
from ptah.testing import BaseTestCase


class TestTimezoneField(BaseTestCase):

    _includes = ['ptah.form']

    def test_timezone_schema_to_form(self):
        from ptah.form import null, TimezoneField

        typ = TimezoneField('test')

        self.assertTrue(typ.to_form(null) is null)
        self.assertEqual(typ.to_form(pytz.UTC), 'utc')

    def test_timezone_schema_to_field(self):
        from ptah.form import null, Invalid, TimezoneField

        typ = TimezoneField('test')
        loc_dt = datetime(2002, 10, 27, 1, 30, 00)

        self.assertTrue(typ.to_field(null) is null)
        self.assertTrue(typ.to_field('') is null)

        # special case for 'GMT+X' timezones
        self.assertEqual(repr(typ.to_field('GMT+6')),
                         "<StaticTzInfo 'Etc/GMT+6'>")
        self.assertEqual(repr(typ.to_field('gmt+6')),
                         "<StaticTzInfo 'Etc/GMT+6'>")

        # general timezones
        self.assertEqual(typ.to_field('US/Central') \
                            .localize(loc_dt, is_dst=False).strftime('%Z%z'),
                         "CST-0600")

        self.assertEqual(typ.to_field('us/central') \
                            .localize(loc_dt, is_dst=False).strftime('%Z%z'),
                         "CST-0600")

        # unknown timezone
        self.assertRaises(Invalid, typ.to_field, 'unknown')
