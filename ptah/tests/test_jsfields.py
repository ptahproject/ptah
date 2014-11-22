import ptah.form
from ptah.testing import PtahTestCase
from pyramid.compat import text_type


def invalid_exc(func, *arg, **kw):
    from ptah.form import Invalid
    try:
        func(*arg, **kw)
    except Invalid as e:
        return e
    else:
        raise AssertionError('Invalid not raised')


class TestJSDateTimeField(PtahTestCase):

    def _makeOne(self, **kw):
        from ptah.jsfields import JSDateTimeField
        return JSDateTimeField('test', **kw)

    def test_serialize_null(self):
        typ = self._makeOne()
        result = typ.to_form(ptah.form.null)
        self.assertEqual(result, ptah.form.null)

    def test_serialize_with_garbage(self):
        typ = self._makeOne()
        e = invalid_exc(typ.to_form, 'garbage')
        self.assertEqual(text_type(e), '"garbage" is not a datetime object')

    def test_serialize_with_date(self):
        import datetime
        typ = self._makeOne()
        dt = datetime.datetime.now()
        date = dt.date()
        result = typ.to_form(date)
        expected = dt.date().strftime('%Y-%m-%d %H:%M')
        self.assertEqual(result, expected)

    def test_serialize_with_datetime(self):
        import datetime
        typ = self._makeOne()
        dt = datetime.datetime.now()
        result = typ.to_form(dt)
        expected = dt.strftime('%Y-%m-%d %H:%M')
        self.assertEqual(result, expected)

    def test_deserialize_invalid(self):
        typ = self._makeOne()
        e = invalid_exc(typ.to_field, 'garbage')
        self.assertTrue('Invalid' in e.msg)

    def test_deserialize_invalid_weird(self):
        typ = self._makeOne()
        e = invalid_exc(typ.to_field, '10-10-10 10.10')
        self.assertTrue('Invalid' in e.msg)

    def test_deserialize_null(self):
        typ = self._makeOne()
        result = typ.to_field(ptah.form.null)
        self.assertEqual(result, ptah.form.null)

    def test_deserialize_empty(self):
        typ = self._makeOne()
        result = typ.to_field('')
        self.assertEqual(result, ptah.form.null)

    def test_deserialize_success_date(self):
        import datetime
        typ = self._makeOne()
        dt = datetime.datetime.now(typ.default_tzinfo)
        iso = dt.date().isoformat()
        result = typ.to_field(iso)
        self.assertEqual(result.isoformat(), dt.strftime('%Y-%m-%dT00:00:00+00:00'))

    def test_deserialize_success_datetime(self):
        import datetime
        typ = self._makeOne()
        dt = datetime.datetime.now(typ.default_tzinfo)
        iso = dt.isoformat()
        result = typ.to_field(iso)
        self.assertEqual(result.isoformat(), dt.isoformat())


class TestJSDateField(PtahTestCase):

    def _makeOne(self, **kw):
        from ptah.jsfields import JSDateField
        return JSDateField('test', **kw)

    def test_serialize_null(self):
        typ = self._makeOne()
        result = typ.to_form(ptah.form.null)
        self.assertEqual(result, ptah.form.null)

    def test_serialize_with_garbage(self):
        typ = self._makeOne()
        e = invalid_exc(typ.to_form, 'garbage')
        self.assertEqual(text_type(e), '"garbage" is not a date object')

    def test_serialize_with_date(self):
        import datetime
        typ = self._makeOne()
        date = datetime.date.today()
        result = typ.to_form(date)
        expected = date.isoformat()
        self.assertEqual(result, expected)

    def test_serialize_with_datetime(self):
        import datetime
        typ = self._makeOne()
        dt = datetime.datetime.now()
        result = typ.to_form(dt)
        expected = dt.date().isoformat()
        self.assertEqual(result, expected)

    def test_deserialize_invalid(self):
        typ = self._makeOne()
        e = invalid_exc(typ.to_field, 'garbage')
        self.assertTrue('Invalid' in e.msg)

    def test_deserialize_invalid_weird(self):
        typ = self._makeOne()
        e = invalid_exc(typ.to_field, '10-10-10-10')
        self.assertTrue('Invalid' in e.msg)

    def test_deserialize_null(self):
        typ = self._makeOne()
        result = typ.to_field(ptah.form.null)
        self.assertEqual(result, ptah.form.null)

    def test_deserialize_empty(self):
        typ = self._makeOne()
        result = typ.to_field('')
        self.assertEqual(result, ptah.form.null)

    def test_deserialize_success_date(self):
        import datetime
        typ = self._makeOne()
        date = datetime.date.today()
        iso = date.isoformat()
        result = typ.to_field(iso)
        self.assertEqual(result, date)

    def test_deserialize_success_datetime(self):
        import datetime

        dt = datetime.datetime.now()
        typ = self._makeOne()
        iso = dt.date().isoformat()
        result = typ.to_field(iso)
        self.assertEqual(result.isoformat(), dt.date().isoformat())
