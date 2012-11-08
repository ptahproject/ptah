import pform
from ptah.testing import PtahTestCase


def invalid_exc(func, *arg, **kw):
    from pform import Invalid
    try:
        func(*arg, **kw)
    except Invalid as e:
        return e
    else:
        raise AssertionError('Invalid not raised') # pragma: no cover


def strip(str):
    return ' '.join(s.strip() for s in str.split())


class TestJSDateTimeField(PtahTestCase):

    def _makeOne(self, name, **kw):
        from ptah.jsfields import JSDateTimeField
        return JSDateTimeField(name, **kw)

    def test_fields_jsdatetime_update(self):
        from datetime import datetime

        request = self.request
        field = self._makeOne('test')

        f = field.bind(request, '', pform.null, {})
        f.update()

        self.assertEqual(f.date_part, '')
        self.assertEqual(f.time_part, '')

        dt = datetime(2011, 1, 1, 10, 10)

        f = field.bind(request, '', dt, {})
        f.update()

        self.assertEqual(f.date_part, '01/01/2011')
        self.assertEqual(f.time_part, '10:10 AM')

    def test_fields_jsdatetime_extract(self):
        request = self.request
        field = self._makeOne('test')

        f = field.bind(request, '', pform.null, {})
        f.update()
        self.assertIs(f.extract('default'), 'default')

        f = field.bind(request, '', pform.null, {'test.date': ''})
        f.update()
        self.assertIs(f.extract(), pform.null)

        f = field.bind(request, '', pform.null,
                       {'test.date': '12/01/2011'})
        f.update()
        self.assertIs(f.extract('default'), 'default')

        f = field.bind(request, '', pform.null,
                       {'test.date': '12/01/2011',
                        'test.time': ''})
        f.update()
        self.assertIs(f.extract(), pform.null)

        f = field.bind(request, '', pform.null,
                       {'test.date': 'exception',
                        'test.time': 'exception'})
        f.update()
        self.assertIs(f.extract(), pform.null)

        f = field.bind(request, '', pform.null,
                       {'test.date': '12/01/2011',
                        'test.time': '10:10 AM'})
        f.update()
        self.assertEqual(f.extract(), '2011-12-01T10:10:00')


class TestJSDateField(PtahTestCase):

    def _makeOne(self, **kw):
        from ptah.jsfields import JSDateField
        return JSDateField('test', **kw)

    def test_serialize_null(self):
        typ = self._makeOne()
        result = typ.to_form(pform.null)
        self.assertEqual(result, pform.null)

    def test_serialize_with_garbage(self):
        typ = self._makeOne()
        e = invalid_exc(typ.to_form, 'garbage')
        self.assertEqual(e.msg.interpolate(),
                         '"garbage" is not a date object')

    def test_serialize_with_date(self):
        import datetime
        typ = self._makeOne()
        date = datetime.date.today()
        result = typ.to_form(date)
        expected = date.strftime('%m/%d/%Y')
        self.assertEqual(result, expected)

    def test_serialize_with_datetime(self):
        import datetime
        typ = self._makeOne()
        dt = datetime.datetime.now()
        result = typ.to_form(dt)
        expected = dt.strftime('%m/%d/%Y')
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
        result = typ.to_field(pform.null)
        self.assertEqual(result, pform.null)

    def test_deserialize_empty(self):
        typ = self._makeOne()
        result = typ.to_field('')
        self.assertEqual(result, pform.null)

    def test_deserialize_success_date(self):
        import datetime
        typ = self._makeOne()
        date = datetime.date.today()
        iso = date.strftime('%m/%d/%Y')
        result = typ.to_field(iso)
        self.assertEqual(result, date)

    def test_deserialize_success_datetime(self):
        import datetime

        dt = datetime.datetime.now()
        typ = self._makeOne()
        iso = dt.strftime('%m/%d/%Y')
        result = typ.to_field(iso)
        self.assertEqual(result.isoformat(), dt.date().isoformat())
