import pytz
from ptah.testing import PtahTestCase


class TestTimezoneField(PtahTestCase):

    def test_timezone_schema_serialize(self):
        from ptah.form import null, TimezoneField

        typ = TimezoneField('test')

        self.assertTrue(typ.serialize(null) is null)
        self.assertEqual(typ.serialize(pytz.UTC), 'UTC')

    def test_timezone_schema_deserialize(self):
        from ptah.form import null, Invalid, TimezoneField

        typ = TimezoneField('test')

        self.assertTrue(typ.deserialize(null) is null)
        self.assertTrue(typ.deserialize('') is null)

        # special case for 'GMT+X' timezones
        self.assertEqual(repr(typ.deserialize('GMT+6')),
                         "<StaticTzInfo 'Etc/GMT+6'>")

        # general timezones
        self.assertEqual(repr(typ.deserialize('US/Central')),
                         "<DstTzInfo 'US/Central' CST-1 day, 18:00:00 STD>")

        self.assertEqual(repr(typ.deserialize('us/central')),
                         "<DstTzInfo 'US/Central' CST-1 day, 18:00:00 STD>")

        # unknown timezone
        self.assertRaises(Invalid, typ.deserialize, 'unknown')
