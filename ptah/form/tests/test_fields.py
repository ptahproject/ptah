from unittest import mock
import decimal
from webob.multidict import MultiDict
from pyramid.compat import text_type, NativeIO

import ptah.form
from ptah.form import iso8601

from ptah.testing import strip, BaseTestCase


def invalid_exc(func, *arg, **kw):
    from ptah.form import Invalid
    try:
        func(*arg, **kw)
    except Invalid as e:
        return e
    else:
        raise AssertionError('Invalid not raised')


class TestInputField(BaseTestCase):

    _includes = ['ptah.form']

    def _makeOne(self, name, **kw):
        from ptah.form.fields import InputField
        return InputField(name, **kw)

    def test_fields_text(self):
        request = self.make_request()

        field = self._makeOne('test')
        field = field.bind(request, '', 'content', {})
        field.update()

        self.assertEqual(field.klass, 'form-control')

        field.readonly = True
        field.update()

        self.assertEqual(field.klass, 'form-control disabled')


class TestTextField(BaseTestCase):

    _includes = ['ptah.form']

    def _makeOne(self, name, **kw):
        return ptah.form.TextField(name, title=name.capitalize(), **kw)

    def test_fields_text(self):
        request = self.make_request()

        field = self._makeOne('test')
        field = field.bind(request, '', 'content', {})
        field.update()

        self.assertEqual(field.to_form('value'), 'value')
        self.assertEqual(field.to_field('value'), 'value')

        res = field.render().strip()
        self.assertEqual(
            '<input type="text" class="form-control text-widget" value="content" id="test" name="test" title="Test">',
            res)

        field = self._makeOne('test')
        field = field.bind(request, '', 'content', {'test': 'form'})
        field.update()

        res = field.render().strip()
        self.assertIn(
            '<input type="text" class="form-control text-widget" value="form" id="test" name="test" title="Test">',
            res)


class TestIntegerField(BaseTestCase):

    _includes = ['ptah.form']

    def _makeOne(self, name, **kw):
        return ptah.form.IntegerField(name, title=name.capitalize(), **kw)

    def test_fields_int(self):
        request = self.make_request()

        field = self._makeOne('test')
        field = field.bind(request, '', 10, {})
        field.update()

        self.assertEqual(field.to_form(10), '10')
        self.assertRaises(ptah.form.Invalid, field.to_form, 'value')

        self.assertIs(field.to_field(''), ptah.form.null)
        self.assertEqual(field.to_field('10'), 10)
        self.assertRaises(ptah.form.Invalid, field.to_field, 'value')

        res = field.render().strip()
        self.assertEqual(
            '<input type="text" class="form-control int-widget" value="10" id="test" name="test" title="Test">',
            res)


class TestFloatField(BaseTestCase):

    _includes = ['ptah.form']

    def _makeOne(self, name, **kw):
        return ptah.form.FloatField(name, title=name.capitalize(), **kw)

    def test_fields_float(self):
        request = self.make_request()

        field = self._makeOne('test')
        field = field.bind(request, '', 10.34, {})
        field.update()

        self.assertEqual(field.to_form(10.34), '10.34')
        self.assertRaises(ptah.form.Invalid, field.to_form, 'value')

        self.assertIs(field.to_field(''), ptah.form.null)
        self.assertEqual(field.to_field('10.34'), 10.34)
        self.assertRaises(ptah.form.Invalid, field.to_field, 'value')

        res = field.render().strip()
        self.assertEqual(
            '<input type="text" class="form-control float-widget" value="10.34" id="test" name="test" title="Test">',
            res)


class TestDeciamlField(BaseTestCase):

    _includes = ['ptah.form']

    def _makeOne(self, name, **kw):
        return ptah.form.DecimalField(name, title=name.capitalize(), **kw)

    def test_fields_decimal(self):
        request = self.make_request()

        field = self._makeOne('test')
        field = field.bind(request, '', decimal.Decimal('10.34'), {})
        field.update()

        self.assertEqual(field.to_form(decimal.Decimal('10.34')), '10.34')
        self.assertRaises(ptah.form.Invalid, field.to_form, 'value')

        self.assertIs(field.to_field(''), ptah.form.null)
        self.assertEqual(field.to_field('10.34'), decimal.Decimal('10.34'))
        self.assertRaises(ptah.form.Invalid, field.to_field, 'value')

        res = field.render().strip()
        self.assertEqual(
            '<input type="text" class="form-control decimal-widget" value="10.34" id="test" name="test" title="Test">',
            res)


class TestLinesField(BaseTestCase):

    _includes = ['ptah.form']

    def _makeOne(self, name, **kw):
        return ptah.form.LinesField(name, title=name.capitalize(), **kw)

    def test_fields_linesfield(self):
        request = self.make_request()

        field = self._makeOne('test')
        field = field.bind(request, '', ['1','2','3'], {})
        field.update()

        self.assertEqual(field.to_form(['1','2','3']), '1\n2\n3')
        self.assertRaises(ptah.form.Invalid, field.to_form, 1)

        self.assertIs(field.to_field(''), ptah.form.null)
        self.assertEqual(field.to_field('1\n2\n3'), ['1','2','3'])
        self.assertRaises(ptah.form.Invalid, field.to_field, 5)

        res = field.render().strip()
        self.assertIn(
            '<textarea class="form-control textlines-widget" value="1\n2\n3" id="test" name="test" title="Test" rows="5" cols="40">1\n2\n3</textarea>',
            res)


class TestVocabularyField(BaseTestCase):

    _includes = ['ptah.form']

    def test_ctor(self):
        from ptah.form.fields import VocabularyField

        voc = object()

        self.assertRaises(ValueError, VocabularyField, 'test')
        self.assertRaises(ValueError, VocabularyField, 'test',
                          vocabulary=('test',), voc_factory=voc)

    def test_ctor_convert_vocabulary(self):
        from ptah.form.fields import VocabularyField

        field = VocabularyField('test', vocabulary=('one', 'two'))
        self.assertIsInstance(field.vocabulary, ptah.form.Vocabulary)
        self.assertIs(field.vocabulary, field.cls.vocabulary)
        self.assertEqual(2, len(field.vocabulary))

    def test_voc_factory(self):
        from ptah.form.fields import VocabularyField

        voc = object()
        def factory(context):
            return voc

        field = VocabularyField('test', voc_factory=factory)
        clone = field.bind(self.request, 'p.', None, None)
        self.assertIs(clone.vocabulary, voc)

    def test_voc_factory_context(self):
        from ptah.form.fields import VocabularyField

        voc = object()
        data = []
        def factory(c):
            data.append(c)
            return voc

        field = VocabularyField('test', voc_factory=factory)
        field.bind(self.request, 'p.', None, None)
        self.assertIsNone(data[-1])

        context = object()
        field.bind(self.request, 'p.', None, None, context)
        self.assertIs(data[-1], context)

    def test_voc_factory_mapper(self):
        from ptah.form.fields import voc_factory_mapper
        m = mock.Mock()

        ob = object()
        m.request = ob
        def fn(request):
            return request

        self.assertIs(ob, voc_factory_mapper(fn)(m))

        ob = object()
        m.context = ob
        def fn(context):
            return context

        self.assertIs(ob, voc_factory_mapper(fn)(m))

        ob = object()
        m.content = ob
        def fn(content):
            return content

        self.assertIs(ob, voc_factory_mapper(fn)(m))

        ob = object()
        m.content = ob
        def fn(arg):
            return arg

        self.assertIs(m, voc_factory_mapper(fn)(m))

    def test_takes_one_arg(self):
        from ptah.form.fields import takes_one_arg
        def fn(arg):
            return arg

        self.assertTrue(takes_one_arg(fn, 'arg'))
        self.assertFalse(takes_one_arg(fn, 'context'))

    @mock.patch('ptah.form.fields.inspect')
    def test_takes_one_arg(self, m_inspect):
        m_inspect.getargspec.side_effect = TypeError

        from ptah.form.fields import takes_one_arg
        def fn(arg):
            return arg

        self.assertFalse(takes_one_arg(fn, 'arg'))

    def test_vocabulary_field(self):
        voc = ptah.form.Vocabulary(
            (1, 'one', 'One'),
            (2, 'two', 'Two'),
            (3, 'three', 'Three'))

        self.assertRaises(ValueError, ptah.form.VocabularyField, 'test')
        self.assertRaises(
            NotImplementedError,
            ptah.form.VocabularyField('test', vocabulary=voc).is_checked,
            voc.get_term(1))

        class MyVocabularyField(ptah.form.VocabularyField):
            def is_checked(self, term):
                return term.token == self.form_value

        field = MyVocabularyField('test', vocabulary=voc)
        field.form_value = 'one'

        self.assertTrue(field.is_checked(voc.get_term(1)))
        self.assertFalse(field.is_checked(voc.get_term(2)))

        field.id = 'test'
        field.form_value = ptah.form.null
        field.update_items()

        self.assertEqual(field.items,
                         [{'checked': False,
                           'description': None,
                           'id': 'test-0',
                           'label': 'One',
                           'name': 'test',
                           'value': 'one'},
                          {'checked': False,
                           'description': None,
                           'id': 'test-1',
                           'label': 'Two',
                           'name': 'test',
                           'value': 'two'},
                          {'checked': False,
                           'description': None,
                           'id': 'test-2',
                           'label': 'Three',
                           'name': 'test',
                           'value': 'three'}])

        field.form_value = 'one'
        field.update_items()
        self.assertEqual(field.items,
                         [{'checked': True,
                           'description': None,
                           'id': 'test-0',
                           'label': 'One',
                           'name': 'test',
                           'value': 'one'},
                          {'checked': False,
                           'description': None,
                           'id': 'test-1',
                           'label': 'Two',
                           'name': 'test',
                           'value': 'two'},
                          {'checked': False,
                           'description': None,
                           'id': 'test-2',
                           'label': 'Three',
                           'name': 'test',
                           'value': 'three'}])


class TestBaseChoiceField(BaseTestCase):

    _includes = ['ptah.form']

    def _makeOne(self, name, **kw):
        return ptah.form.BaseChoiceField(name, **kw)

    def test_basechoice(self):
        request = self.make_request()

        voc = ptah.form.Vocabulary(
            (1, 'one', 'One'),
            (2, 'two', 'Two'),
            (3, 'three', 'Three'))

        field = self._makeOne('test', vocabulary=voc)
        field = field.bind(request, '', 1, {})
        field.update()

        self.assertIs(field.extract(), ptah.form.null)

        field.params = {'test': '--NOVALUE--'}
        self.assertIs(field.extract(), ptah.form.null)

        field.params = {'test': 'three'}
        self.assertIs(field.extract(), 'three')

        self.assertEqual(field.to_form(1), 'one')
        self.assertRaises(ptah.form.Invalid, field.to_form, 10)
        self.assertRaises(ptah.form.Invalid, field.to_form, [1, 10])

        self.assertIs(field.to_field(''), ptah.form.null)
        self.assertEqual(field.to_field('one'), 1)
        self.assertRaises(ptah.form.Invalid, field.to_field, 5)
        self.assertRaises(ptah.form.Invalid, field.to_field, ['one','five'])


class TestBaseMultiChoiceField(BaseTestCase):

    _includes = ['ptah.form']

    def _makeOne(self, name, **kw):
        return ptah.form.BaseMultiChoiceField(name, **kw)

    def test_basemultichoice(self):
        request = self.make_request()

        self.assertRaises(ValueError, self._makeOne, 'test')

        voc = ptah.form.Vocabulary(
            (1, 'one', 'One'),
            (2, 'two', 'Two'),
            (3, 'three', 'Three'))

        orig_field = self._makeOne('test', vocabulary=voc)
        field = orig_field.bind(request, '', [1,3], {})
        field.update()

        self.assertEqual(field.to_form([1,2]), ['one','two'])
        self.assertRaises(ptah.form.Invalid, field.to_form, 1)
        self.assertRaises(ptah.form.Invalid, field.to_form, [1, 10])

        self.assertIs(field.to_field(''), ptah.form.null)
        self.assertEqual(field.to_field(['one','three']), [1,3])
        self.assertRaises(ptah.form.Invalid, field.to_field, 5)
        self.assertRaises(ptah.form.Invalid, field.to_field, ['one','five'])

        field = orig_field.bind(request, '', ptah.form.null, {})
        field.update()
        self.assertEqual(field.form_value, [])

        field = orig_field.bind(request, '', [1], {})
        field.update()
        self.assertEqual(field.form_value, ['one'])

        self.assertIs(field.extract(), ptah.form.null)

        field.params = MultiDict((('test', field.no_value_token),
                                  ('test', 'one')))
        self.assertEqual(field.extract(), ['one'])


class TestChoiceField(BaseTestCase):

    _includes = ['ptah.form']

    def _makeOne(self, name, **kw):
        return ptah.form.ChoiceField(name, **kw)

    def test_vocabulary_field(self):
        request = self.make_request()

        voc = ptah.form.Vocabulary(
            (1, 'one', 'One'),
            (2, 'two', 'Two'))

        field = self._makeOne('test', vocabulary=voc)
        field = field.bind(request, '', 1, {})
        field.id = 'test'
        field.update()

        self.assertEqual(field.items,
                         [{'checked': 'checked',
                           'description': None,
                           'id': 'test-0',
                           'label': 'One',
                           'name': 'test',
                           'value': 'one'},
                          {'checked': None,
                           'description': None,
                           'id': 'test-1',
                           'label': 'Two',
                           'name': 'test',
                           'value': 'two'}])

        field = self._makeOne('test', missing=2, required=False, vocabulary=voc)
        field = field.bind(request, '', 1, {})
        field.id = 'test'
        field.update()

        self.assertEqual(field.items,
                         [{'checked': None,
                           'description': '',
                           'id': 'test-novalue',
                           'label': 'select a value ...',
                           'name': 'test',
                           'value': '--NOVALUE--'},
                          {'checked': 'checked',
                           'description': None,
                           'id': 'test-0',
                           'label': 'One',
                           'name': 'test',
                           'value': 'one'},
                          {'checked': None,
                           'description': None,
                           'id': 'test-1',
                           'label': 'Two',
                           'name': 'test',
                           'value': 'two'}])


class TestMultiChoiceField(BaseTestCase):

    _includes = ['ptah.form']

    def _makeOne(self, name, **kw):
        return ptah.form.MultiChoiceField(name, **kw)

    def test_fields_decimal(self):
        request = self.make_request()

        voc = ptah.form.Vocabulary(
            (1, 'one', 'One'),
            (2, 'two', 'Two'),
            (3, 'three', 'Three'))

        field = self._makeOne('test', vocabulary=voc)
        field = field.bind(request, '', [1,3], {})
        field.update()


class TestDateTime(BaseTestCase):

    _includes = ['ptah.form']

    def _makeOne(self, name='test', *arg, **kw):
        return ptah.form.DateTimeField(name, request=self.request, *arg, **kw)

    def _dt(self):
        import datetime
        return datetime.datetime(2010, 4, 26, 10, 48)

    def _today(self):
        import datetime
        return datetime.date.today()

    def test_ctor_default_tzinfo_None(self):
        typ = self._makeOne()
        self.assertEqual(typ.default_tzinfo.__class__, iso8601.Utc)

    def test_ctor_default_tzinfo_non_None(self):
        tzinfo = iso8601.FixedOffset(1, 0, 'myname')
        typ = self._makeOne(default_tzinfo=tzinfo)
        self.assertEqual(typ.default_tzinfo, tzinfo)

    def test_to_form_null(self):
        typ = self._makeOne()
        result = typ.to_form(ptah.form.null)
        self.assertEqual(result, ptah.form.null)

    def test_to_form_with_garbage(self):
        typ = self._makeOne()
        e = invalid_exc(typ.to_form, 'garbage')
        self.assertEqual(str(e), '"garbage" is not a datetime object')

    def test_to_form_with_date(self):
        import datetime
        typ = self._makeOne()
        date = self._today()
        result = typ.to_form(date)
        expected = datetime.datetime.combine(date, datetime.time())
        expected = expected.replace(tzinfo=typ.default_tzinfo).isoformat()
        self.assertEqual(result, expected)

    def test_to_form_with_naive_datetime(self):
        typ = self._makeOne()
        dt = self._dt()
        result = typ.to_form(dt)
        expected = dt.replace(tzinfo=typ.default_tzinfo).isoformat()
        self.assertEqual(result, expected)

    def test_to_form_with_none_tzinfo_naive_datetime(self):
        typ = self._makeOne(default_tzinfo=None)
        dt = self._dt()
        result = typ.to_form(dt)
        self.assertEqual(result, dt.isoformat())

    def test_to_form_with_tzware_datetime(self):
        typ = self._makeOne()
        dt = self._dt()
        tzinfo = iso8601.FixedOffset(1, 0, 'myname')
        dt = dt.replace(tzinfo=tzinfo)
        result = typ.to_form(dt)
        expected = dt.isoformat()
        self.assertEqual(result, expected)

    def test_to_field_date(self):
        import datetime
        date = self._today()
        typ = self._makeOne()
        formatted = date.isoformat()
        result = typ.to_field(formatted)
        expected = datetime.datetime.combine(result, datetime.time())
        tzinfo = iso8601.Utc()
        expected = expected.replace(tzinfo=tzinfo)
        self.assertEqual(result.isoformat(), expected.isoformat())

    def test_to_field_invalid_ParseError(self):
        typ = self._makeOne()
        e = invalid_exc(typ.to_field, 'garbage')
        self.assertTrue('Invalid' in e.msg)

    def test_to_field_null(self):
        typ = self._makeOne()
        result = typ.to_field(ptah.form.null)
        self.assertEqual(result, ptah.form.null)

    def test_to_field_missing(self):
        typ = self._makeOne()
        result = typ.to_field('')
        self.assertEqual(result, ptah.form.null)

    def test_to_field_success(self):
        typ = self._makeOne()
        dt = self._dt()
        tzinfo = iso8601.FixedOffset(1, 0, 'myname')
        dt = dt.replace(tzinfo=tzinfo)
        iso = dt.isoformat()
        result = typ.to_field(iso)
        self.assertEqual(result.isoformat(), iso)

    def test_to_field_naive_with_default_tzinfo(self):
        tzinfo = iso8601.FixedOffset(1, 0, 'myname')
        typ = self._makeOne(default_tzinfo=tzinfo)
        dt = self._dt()
        dt_with_tz = dt.replace(tzinfo=tzinfo)
        iso = dt.isoformat()
        result = typ.to_field(iso)
        self.assertEqual(result.isoformat(), dt_with_tz.isoformat())

    def test_to_field_none_tzinfo(self):
        typ = self._makeOne(default_tzinfo=None)
        dt = self._dt()
        iso = dt.isoformat()
        result = typ.to_field(iso)
        self.assertEqual(result.isoformat(), dt.isoformat())


class TestDate(BaseTestCase):

    _includes = ['ptah.form']

    def _makeOne(self, name='test', *arg, **kw):
        return ptah.form.DateField(name, request=self.request, *arg, **kw)

    def _dt(self):
        import datetime
        return datetime.datetime(2010, 4, 26, 10, 48)

    def _today(self):
        import datetime
        return datetime.date.today()

    def test_to_form_null(self):
        val = ptah.form.null
        typ = self._makeOne()
        result = typ.to_form(val)
        self.assertEqual(result, ptah.form.null)

    def test_to_form_with_garbage(self):
        typ = self._makeOne()
        e = invalid_exc(typ.to_form, 'garbage')
        self.assertEqual(str(e), '"garbage" is not a date object')

    def test_to_form_with_date(self):
        typ = self._makeOne()
        date = self._today()
        result = typ.to_form(date)
        expected = date.isoformat()
        self.assertEqual(result, expected)

    def test_to_form_with_datetime(self):
        typ = self._makeOne()
        dt = self._dt()
        result = typ.to_form(dt)
        expected = dt.date().isoformat()
        self.assertEqual(result, expected)

    def test_to_field_invalid_ParseError(self):
        typ = self._makeOne()
        e = invalid_exc(typ.to_field, 'garbage')
        self.assertTrue('Invalid' in e.msg)

    def test_to_field_invalid_weird(self):
        typ = self._makeOne()
        e = invalid_exc(typ.to_field, '10-10-10-10')
        self.assertTrue('Invalid' in e.msg)

    def test_to_field_null(self):
        typ = self._makeOne()
        result = typ.to_field(ptah.form.null)
        self.assertEqual(result, ptah.form.null)

    def test_to_field_missing(self):
        typ = self._makeOne()
        result = typ.to_field('')
        self.assertEqual(result, ptah.form.null)

    def test_to_field_success_date(self):
        typ = self._makeOne()
        date = self._today()
        iso = date.isoformat()
        result = typ.to_field(iso)
        self.assertEqual(result.isoformat(), iso)

    def test_to_field_success_datetime(self):
        dt = self._dt()
        typ = self._makeOne()
        iso = dt.isoformat()
        result = typ.to_field(iso)
        self.assertEqual(result.isoformat(), dt.date().isoformat())


class TestFileField(BaseTestCase):

    _includes = ['ptah.form']

    def _makeOne(self, name, **kw):
        from ptah.form.fields import FileField
        return FileField(name, **kw)

    def test_fields_text(self):
        request = self.make_request()

        field = self._makeOne('test')
        field = field.bind(request, '', 'content', {})
        field.update()

        self.assertIs(field.extract(), ptah.form.null)

        class FileStorage:

            def __init__(self, fp, filename, mt, s):
                self.file = fp
                self.filename = filename
                self.type = mt
                self.length = s

        fs = FileStorage(NativeIO(), 'test.jpg', 'image/jpeg', 1024)

        field = self._makeOne('test')
        field = field.bind(request, '', 'content', {'test': fs})
        field.update()

        res = field.extract()
        self.assertIs(type(res), dict)
        self.assertEqual(res['filename'], 'test.jpg')

    def test_fields_html5(self):
        request = self.make_request()

        field = self._makeOne('test')
        field = field.bind(request, '', 'content', {})
        field.update()

        self.assertIs(field.extract(), ptah.form.null)

        params = {
            'test': text_type(' '*1024),
            'test-filename': 'test.jpg',
            'test-mimetype': 'image/jpeg'}

        field = self._makeOne('test')
        field = field.bind(request, '', 'content', params)
        field.update()

        res = field.extract()
        self.assertIs(type(res), dict)
        self.assertEqual(res['filename'], 'test.jpg')

    def test_validate_null(self):
        request = self.make_request()

        field = self._makeOne('test', allowed_types=('image/jpg',))
        field = field.bind(request, '', 'content', {})
        field.required = False

        self.assertIsNone(field.validate(ptah.form.null))

    def test_validate_allowed_types(self):
        request = self.make_request()

        field = self._makeOne('test', allowed_types=('image/jpg',))
        field = field.bind(request, '', 'content', {})

        value = {'mimetype': 'image/png'}

        with self.assertRaises(ptah.form.Invalid) as cm:
            field.validate(value)

        self.assertEqual('Unknown file type.', cm.exception.msg)

    def test_validate_max_size(self):
        request = self.make_request()

        field = self._makeOne('test', max_size=1)
        field = field.bind(request, '', 'content', {})

        fp = NativeIO('          ')

        with self.assertRaises(ptah.form.Invalid) as cm:
            field.validate({'fp': fp})

        self.assertEqual('Maximum file size exceeded.', cm.exception.msg)


class TestOptionsField(BaseTestCase):

    _includes = ['ptah.form']

    def test_ctor(self):
        field = ptah.form.OptionsField(
            'test',
            fields=(ptah.form.TextField('name'),
                    ptah.form.TextField('address')))
        self.assertEqual('test', field.key)

        field = ptah.form.OptionsField(
            'test', key='option_key',
            fields=(ptah.form.TextField('name'),
                    ptah.form.TextField('address')))

        self.assertEqual('option_key', field.key)
        self.assertEqual(3, len(field.fields))
        self.assertIn('option_key', field.fields)

        ofield = field.fields['option_key']
        self.assertIsInstance(ofield, ptah.form.RadioField)

        self.assertEqual(2, len(ofield.vocabulary))
        self.assertEqual(
            ['name', 'address'], [t.value for t in ofield.vocabulary])

    def test_to_field(self):
        field = ptah.form.OptionsField(
            'test',
            fields=(ptah.form.TextField('name'),
                    ptah.form.TextField('address')))

        self.assertEqual({'name': '123'},
                         field.to_field({'name': '123'}))


    def test_to_field_with_defaults(self):
        field = ptah.form.OptionsField(
            'test',
            defaults=True,
            fields=(ptah.form.TextField('name'),
                    ptah.form.TextField('address', default='street 123')))

        self.assertEqual({'name':'123', 'address':'street 123', 'test':'name'},
                         field.to_field({'name': '123'}))

    def test_extract(self):
        field = ptah.form.OptionsField(
            'test',
            fields=(ptah.form.TextField('name'),
                    ptah.form.TextField('address')))

        field = field.bind(
            self.request, '', {},
            {'test': 'name',
             'name': 'nikolay',
             'address': 'street 123'})

        self.assertEqual({'name': 'nikolay', 'test': 'name'}, field.extract())

    def test_extract_all(self):
        field = ptah.form.OptionsField(
            'test', extract_all=True,
            fields=(ptah.form.TextField('name'),
                    ptah.form.TextField('address')))

        field = field.bind(
            self.request, '', {},
            {'test': 'name',
             'name': 'nikolay',
             'address': 'street 123'})

        self.assertEqual(
            {'name': 'nikolay', 'address': 'street 123', 'test': 'name'},
            field.extract())

    def test_extract_unknown_option(self):
        field = ptah.form.OptionsField(
            'test',
            fields=(ptah.form.TextField('name'),
                    ptah.form.TextField('address')))

        field = field.bind(
            self.request, '', {},
            {'test': 'unknown',
             'name': 'nikolay',
             'address': 'street 123'})

        self.assertEqual({}, field.extract())

    def test_validate(self):
        field = ptah.form.OptionsField(
            'test',
            fields=(ptah.form.TextField('name'),
                    ptah.form.TextField('address')))

        with self.assertRaises(ptah.form.CompositeError) as cm:
            field.validate({})

        self.assertIn('name', cm.exception)

    def test_validate_(self):
        field = ptah.form.OptionsField(
            'test',
            fields=(ptah.form.TextField('name'),
                    ptah.form.TextField('address')))

        with self.assertRaises(ptah.form.CompositeError) as cm:
            field.validate({'test': 'address', 'name': '123'})

        self.assertIn('address', cm.exception)

    def test_render(self):
        field = ptah.form.OptionsField(
            'test',
            fields=(ptah.form.TextField('name'),
                    ptah.form.TextField('address')))

        field = field.bind(
            self.request, '', {},
            {'test': 'test',
             'name': 'nikolay',
             'address': 'street 123'})

        field.render_widget()
