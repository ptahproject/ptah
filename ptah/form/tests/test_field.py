from pyramid.testing import DummyRequest

import ptah.form
from ptah.testing import PtahTestCase


field = ptah.form.TextField(
    'test', title = 'Test node')

field1 = ptah.form.TextField(
    'test1', title = 'Test node')


class TestField(PtahTestCase):

    def test_field_ctor(self):
        field = ptah.form.Field('test', **{'title': 'Title',
                                      'description': 'Description',
                                      'readonly': True,
                                      'default': 'Default',
                                      'missing': 'Missing',
                                      'preparer': 'Preparer',
                                      'validator': 'validator',
                                      'custom_attr': 'Custom attr'})

        self.assertEqual(field.name, 'test')
        self.assertEqual(field.title, 'Title')
        self.assertEqual(field.description, 'Description')
        self.assertEqual(field.readonly, True)
        self.assertEqual(field.default, 'Default')
        self.assertEqual(field.missing, 'Missing')
        self.assertEqual(field.preparer, 'Preparer')
        self.assertEqual(field.validator, 'validator')
        self.assertEqual(field.custom_attr, 'Custom attr')

        self.assertEqual(repr(field), "Field<test>")

    def test_field_bind(self):
        orig_field = ptah.form.Field(
            'test', **{'title': 'Title',
                       'description': 'Description',
                       'readonly': True,
                       'default': 'Default',
                       'missing': 'Missing',
                       'preparer': 'Preparer',
                       'validator': 'validator',
                       'custom_attr': 'Custom attr'})

        field = orig_field.bind(self.request, 'field.', ptah.form.null, {})

        self.assertEqual(field.request, self.request)
        self.assertEqual(field.value, ptah.form.null)
        self.assertEqual(field.params, {})
        self.assertEqual(field.name, 'field.test')
        self.assertEqual(field.title, 'Title')
        self.assertEqual(field.description, 'Description')
        self.assertEqual(field.readonly, True)
        self.assertEqual(field.default, 'Default')
        self.assertEqual(field.missing, 'Missing')
        self.assertEqual(field.preparer, 'Preparer')
        self.assertEqual(field.validator, 'validator')
        self.assertEqual(field.custom_attr, 'Custom attr')
        self.assertIsNone(field.context)
        self.assertIsNone(orig_field.context)

        self.assertEqual(repr(field), "Field<field.test>")

        context = object()
        field = orig_field.bind(object(), 'field.', ptah.form.null, {}, context)
        self.assertIs(field.context, context)

    def test_field_cant_bind(self):
        """
        Can't bind already bound field
        """
        orig_field = ptah.form.Field('test')
        field = orig_field.bind(self.request, 'field.', ptah.form.null, {})

        self.assertRaises(TypeError, field.bind)

    def test_field_validate(self):
        field = ptah.form.Field('test')

        self.assertIsNone(field.validate(''))
        self.assertRaises(ptah.form.Invalid, field.validate, field.missing)

        def validator(field, value):
            raise ptah.form.Invalid('msg', field)

        field = ptah.form.Field('test', validator=validator)
        self.assertRaises(ptah.form.Invalid, field.validate, '')

    def test_field_validate_bound_field(self):
        orig = ptah.form.Field('test')
        field = orig.bind(self.request, 'field.', ptah.form.null, {})

        self.assertIsNone(field.validate(''))
        self.assertRaises(ptah.form.Invalid, field.validate, field.missing)

        def validator(field, value):
            raise ptah.form.Invalid('msg', field)

        orig = ptah.form.Field('test', validator=validator)
        field = orig.bind(self.request, 'field.', ptah.form.null, {})
        self.assertRaises(ptah.form.Invalid, field.validate, '')

    def test_field_validate_type(self):
        field = ptah.form.Field('test')
        field.typ = int

        self.assertRaises(ptah.form.Invalid, field.validate, '')

    def test_field_validate_missing(self):
        field = ptah.form.Field('test')
        field.missing = ''

        with self.assertRaises(ptah.form.Invalid) as cm:
            field.validate('')
        self.assertEqual(field.error_required, cm.exception.msg)

        field.missing = 'test'
        with self.assertRaises(ptah.form.Invalid) as cm:
            field.validate('test')
        self.assertEqual(field.error_required, cm.exception.msg)

    def test_field_validate_null(self):
        field = ptah.form.Field('test')
        field.missing = ''

        with self.assertRaises(ptah.form.Invalid) as cm:
            field.validate(ptah.form.null)
        self.assertEqual(field.error_required, cm.exception.msg)

    def test_field_extract(self):
        field = ptah.form.Field('test')

        widget = field.bind(object(), 'field.', ptah.form.null, {})

        self.assertIs(widget.extract(), ptah.form.null)

        widget = field.bind(object, 'field.', ptah.form.null, {'field.test':'TEST'})
        self.assertIs(widget.extract(), 'TEST')

    def test_field_update_value(self):
        class MyField(ptah.form.Field):
            def to_form(self, value):
                return value
            def to_field(self, value):
                return value

        request = object()

        field = MyField('test')
        widget = field.bind(request, 'field.', ptah.form.null, {})
        widget.update()
        self.assertIs(widget.form_value, None)

        field = MyField('test', default='default value')
        widget = field.bind(request, 'field.', ptah.form.null, {})
        widget.update()
        self.assertIs(widget.form_value, 'default value')

        field = MyField('test', default='default value')
        widget = field.bind(request, 'field.', 'content value', {})
        widget.update()
        self.assertIs(widget.form_value, 'content value')

        widget = field.bind(
            request, 'field.', ptah.form.null, {'field.test': 'form value'})
        widget.update()
        self.assertEqual(widget.form_value, 'form value')

    def test_field_update_with_error(self):
        class MyField(ptah.form.Field):
            def to_form(self, value):
                raise ptah.form.Invalid('Invalid value', self)

        request = DummyRequest()

        field = MyField('test')
        widget = field.bind(request, 'field.', '12345', {})
        widget.update()
        self.assertIs(widget.form_value, None)

    def test_field_flatten(self):
        self.assertEqual({'test': 'val'}, ptah.form.Field('test').flatten('val'))

    def test_field_get_error(self):
        err = ptah.form.Invalid('error')

        field = ptah.form.Field('test')
        field.error = err

        self.assertIs(field.get_error(), err)
        self.assertIsNone(field.get_error('test'))

    def test_field_get_error_suberror(self):
        err = ptah.form.Invalid('error')
        err1 = ptah.form.Invalid('error2', name='test')
        err['test'] = err1

        field = ptah.form.Field('test')
        field.error = err

        self.assertIs(field.get_error('test'), err1)


class TestFieldFactory(PtahTestCase):

    def test_field_factory(self):
        class MyField(ptah.form.Field):
            pass

        self.config.provide_form_field('my-field', MyField)

        field = ptah.form.FieldFactory(
            'my-field', 'test', title='Test field')

        self.assertEqual(field.__field__, 'my-field')

        content = object()
        params = object()

        widget = field.bind(self.request, 'field.', content, params)

        self.assertIsInstance(widget, MyField)
        self.assertIs(widget.request, self.request)
        self.assertIs(widget.value, content)
        self.assertIs(widget.params, params)
        self.assertEqual(widget.name, 'field.test')

    def test_field_no_factory(self):
        field = ptah.form.FieldFactory(
            'new-field', 'test', title='Test field')

        self.assertRaises(
            TypeError, field.bind, self.request, '', object(), object())
