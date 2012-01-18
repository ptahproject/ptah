from ptah import form
from ptah.testing import PtahTestCase


field = form.TextField(
    'test', title = 'Test node')

field1 = form.TextField(
    'test1', title = 'Test node')


class TestFieldset(PtahTestCase):

    def test_fieldset_name_title(self):
        fieldset = form.Fieldset(field)

        self.assertEqual(fieldset.name, '')
        self.assertEqual(fieldset.title, '')
        self.assertEqual(fieldset.prefix, '')

        fieldset = form.Fieldset(field1, name='othername', title='Other name')

        self.assertEqual(fieldset.name, 'othername')
        self.assertEqual(fieldset.title, 'Other name')

    def test_fieldset_nested(self):
        fieldset = form.Fieldset(
            field,
            form.Fieldset(name='fs', *(field,)))

        self.assertEqual(fieldset['fs'].name, 'fs')
        self.assertEqual(fieldset['fs'].prefix, 'fs.')

    def test_fieldset_fields(self):
        fieldset = form.Fieldset(field, field1)

        self.assertEqual(list(fieldset.fields()), [field, field1])

    def test_fieldset_append_simple(self):
        fieldset = form.Fieldset(field, name='test')

        self.assertIn('test', fieldset)
        self.assertEqual(fieldset.prefix, 'test.')

        self.assertIs(fieldset['test'], field)

        self.assertRaises(ValueError, fieldset.append, field)
        self.assertRaises(TypeError, fieldset.append, object())

    def test_fieldset_append_fieldset(self):
        fieldset = form.Fieldset(field, name='schema')
        self.assertEqual(list(fieldset.fieldsets()), [fieldset])

        fs = form.Fieldset(field1, name='schema2', )

        fieldset.append(fs)
        self.assertEqual(len(list(fieldset.fieldsets())), 2)

        self.assertIn('schema2', fieldset)
        self.assertIs(fieldset['schema2'], fs)
        self.assertRaises(ValueError, fieldset.append, fs)

    def test_fieldset_select(self):
        fieldset = form.Fieldset(field, field1)

        newfs = fieldset.select('test')
        self.assertNotIn('test1', newfs)
        self.assertEqual(list(newfs.keys()), ['test'])

    def test_fieldset_omit(self):
        fieldset = form.Fieldset(field, field1)

        newfs = fieldset.omit('test')
        self.assertNotIn('test', newfs)
        self.assertEqual(list(newfs.keys()), ['test1'])

    def test_fieldset_add(self):
        fieldset = form.Fieldset(field)
        fieldset = fieldset + form.Fieldset(field1)

        self.assertIn('test', fieldset)
        self.assertIn('test1', fieldset)
        self.assertEqual(list(fieldset.keys()), ['test', 'test1'])

    def test_fieldset_iadd(self):
        fieldset = form.Fieldset(field)
        fieldset += form.Fieldset(field1)

        self.assertIn('test', fieldset)
        self.assertIn('test1', fieldset)
        self.assertEqual(list(fieldset.keys()), ['test', 'test1'])

    def test_fieldset_add_err(self):
        fieldset = form.Fieldset(field)

        self.assertRaises(ValueError, fieldset.__add__, object())

    def test_fieldset_bind(self):
        fieldset = form.Fieldset(field)

        params = object()
        data = {'test': 'CONTENT'}

        fs = fieldset.bind(data, params)

        self.assertIsNot(fieldset, fs)
        self.assertEqual(len(fieldset), len(fs))
        self.assertIs(fs.params, params)
        self.assertIs(fs.data, data)

        self.assertIs(fs['test'].params, params)
        self.assertEqual(fs['test'].value, 'CONTENT')

        fs = fieldset.bind()
        self.assertIsNot(fieldset, fs)
        self.assertEqual(len(fieldset), len(fs))
        self.assertEqual(fs.params, {})
        self.assertEqual(fs.data, {})
        self.assertEqual(fs['test'].params, {})
        self.assertIs(fs['test'].value, form.null)

    def test_fieldset_bind_nested(self):
        fieldset = form.Fieldset(
            field,
            form.Fieldset(name='fs', *(field,)))

        params = object()
        content = {'test': 'CONTENT',
                   'fs': {'test': 'NESTED CONTENT'}}

        fs = fieldset.bind(content, params)

        self.assertEqual(fs['fs']['test'].value, 'NESTED CONTENT')

        fs = fieldset.bind()
        self.assertIs(fs['fs']['test'].value, form.null)

    def test_fieldset_validate(self):
        def validator(fs, data):
            raise form.Invalid(fs, 'msg')

        fieldset = form.Fieldset(field, validator=validator)
        self.assertRaises(form.Invalid, fieldset.validate, {})

        fieldset.bind()
        self.assertRaises(form.Invalid, fieldset.validate, {})

    def _makeOne(self, name, **kw):
        class MyField(form.Field):
            def serialize(self, value): # pragma: no cover
                return value
            def deserialize(self, value):
                return value

        return MyField(name, **kw)

    def test_fieldset_extract_display(self):
        field = self._makeOne('test', mode=form.FORM_DISPLAY)
        fieldset = form.Fieldset(field).bind(None, {'test': 'VALUE'})
        data, errors = fieldset.extract()
        self.assertEqual(data, {})
        self.assertEqual(errors, [])

    def test_fieldset_extract_missing(self):
        field = self._makeOne('test')
        fieldset = form.Fieldset(field).bind()

        data, errors = fieldset.extract()
        self.assertIs(errors[0].field, fieldset['test'])
        self.assertEqual(errors[0].msg, 'Required')

    def test_fieldset_extract_missing_nested(self):
        field = self._makeOne('test')
        fieldset = form.Fieldset(
            field,
            form.Fieldset(name='fs', *(field,))).bind()

        data, errors = fieldset.extract()
        self.assertIs(errors[0].field, fieldset['fs']['test'])
        self.assertIs(errors[1].field, fieldset['test'])
        self.assertEqual(errors[0].msg, 'Required')
        self.assertEqual(errors[1].msg, 'Required')

    def test_fieldset_extract(self):
        field = self._makeOne('test')
        fieldset = form.Fieldset(field).bind(params={'test': 'FORM'})

        data, errors = fieldset.extract()
        self.assertFalse(bool(errors))
        self.assertEqual(data['test'], 'FORM')

    def test_fieldset_extract_nested(self):
        field = self._makeOne('test')
        fieldset = form.Fieldset(
            field,
            form.Fieldset(name='fs', *(field,))
            ).bind(params={'test': 'FORM', 'fs.test': 'NESTED FORM'})

        data, errors = fieldset.extract()
        self.assertFalse(bool(errors))
        self.assertEqual(data['test'], 'FORM')
        self.assertEqual(data['fs']['test'], 'NESTED FORM')

    def test_fieldset_extract_preparer(self):
        def lower(val):
            return val.lower()

        field = self._makeOne('test', preparer=lower)
        fieldset = form.Fieldset(field).bind(params={'test': 'FORM'})

        data, errors = fieldset.extract()
        self.assertEqual(data['test'], 'form')

    def test_fieldset_extract_validate(self):
        def validator(fs, data):
            raise form.Invalid(fs, 'msg')

        field = self._makeOne('test')
        fieldset = form.Fieldset(field, validator=validator)
        fieldset = fieldset.bind(params={'test': 'FORM'})

        data, errors = fieldset.extract()
        self.assertEqual(len(errors), 1)


class TestFieldsetErrors(PtahTestCase):

    def test_fieldset_errors(self):
        err1 = form.Invalid(field, 'error1')
        err2 = form.Invalid(field1, 'error2')

        fieldset = object()

        errors = form.FieldsetErrors(fieldset, err1, err2)
        self.assertIn(err1, errors)
        self.assertIn(err2, errors)
        self.assertIs(errors.fieldset, fieldset)
        self.assertEqual(errors.msg, {'test': 'error1', 'test1': 'error2'})

        self.assertEqual(str(err1), "Invalid: <TextField 'test'>: <error1>")
        self.assertEqual(repr(err1), "Invalid(<TextField 'test'>: <error1>)")
        self.assertEqual(str(form.null), '<widget.null>')

        self.assertFalse(bool(form.required))
        self.assertEqual(repr(form.required), '<widget.required>')


class TestField(PtahTestCase):

    def test_field_ctor(self):
        from ptah import form

        field = form.Field('test', **{'title': 'Title',
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

        self.assertEqual(repr(field), "<Field 'test'>")

    def test_field_bind(self):
        from ptah import form

        orig_field = form.Field(
            'test', **{'title': 'Title',
                       'description': 'Description',
                       'readonly': True,
                       'default': 'Default',
                       'missing': 'Missing',
                       'preparer': 'Preparer',
                       'validator': 'validator',
                       'custom_attr': 'Custom attr'})

        field = orig_field.bind('field.', form.null, {})

        self.assertEqual(field.value, form.null)
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

        self.assertEqual(repr(field), "<Field 'field.test'>")

        context = object()
        field = orig_field.bind('field.', form.null, {}, context)
        self.assertIs(field.context, context)

    def test_field_field_api(self):
        from ptah import form

        field = form.Field('test')

        self.assertRaises(NotImplementedError, field.serialize, '')
        self.assertRaises(NotImplementedError, field.deserialize, '')

    def test_field_validate(self):
        from ptah import form

        field = form.Field('test')

        self.assertIsNone(field.validate(''))
        self.assertRaises(form.Invalid, field.validate, form.required)

        def validator(field, value):
            raise form.Invalid(field, 'msg')

        field = form.Field('test', validator=validator)
        self.assertRaises(form.Invalid, field.validate, '')

    def test_field_extract(self):
        from ptah import form

        field = form.Field('test')

        widget = field.bind('field.', form.null, {})

        self.assertIs(widget.extract(), form.null)
        self.assertIs(widget.extract(default='test'), 'test')

        widget = field.bind('field.', form.null, {'field.test': 'TEST'})
        self.assertIs(widget.extract(), 'TEST')
        self.assertIs(widget.extract(default='test'), 'TEST')

    def test_field_render(self):
        from ptah import form

        class MyField(form.Field):

            def tmpl_input(self, **args):
                return 'INPUT'

            def tmpl_display(self, **args):
                return 'DISPLAY'

        field = MyField('test')
        widget = field.bind('field.', form.null, {})
        widget.request = {}

        widget.mode = form.FORM_INPUT
        self.assertEqual(widget.render({}), 'INPUT')

        widget.mode = form.FORM_DISPLAY
        self.assertEqual(widget.render({}), 'DISPLAY')

    def test_field_update_mode(self):
        from ptah import form

        request = object()
        field = form.Field('test')
        widget = field.bind('field.', form.null, {})

        widget.update(request)
        self.assertEqual(widget.mode, form.FORM_INPUT)

        field = form.Field('test', readonly=True)
        widget = field.bind('field.', form.null, {})

        widget.update(request)
        self.assertEqual(widget.mode, form.FORM_DISPLAY)

        field = form.Field('test', mode=form.FORM_DISPLAY)
        widget = field.bind('field.', form.null, {})

        widget.update(request)
        self.assertEqual(widget.mode, form.FORM_DISPLAY)

    def test_field_update_value(self):
        from ptah import form

        class MyField(form.Field):
            def serialize(self, value):
                return value
            def deserialize(self, value): # pragma: no cover
                return value

        request = object()

        field = MyField('test')
        widget = field.bind('field.', form.null, {})
        widget.update(request)
        self.assertIs(widget.form_value, None)

        field = MyField('test', default='default value')
        widget = field.bind('field.', form.null, {})
        widget.update(request)
        self.assertIs(widget.form_value, 'default value')

        field = MyField('test', default='default value')
        widget = field.bind('field.', 'content value', {})
        widget.update(request)
        self.assertIs(widget.form_value, 'content value')

        widget = field.bind('field.', form.null, {'field.test': 'form value'})
        widget.update(request)
        self.assertEqual(widget.form_value, 'form value')


class TestFieldFactory(PtahTestCase):

    _init_ptah = False

    def test_field_factory(self):
        from ptah import form

        @form.field('my-field')
        class MyField(form.Field):
            pass

        self.init_ptah()

        field = form.FieldFactory(
            'my-field', 'test', title='Test field')

        self.assertEqual(field.__field__, 'my-field')

        content = object()
        params = object()

        widget = field.bind('field.', content, params)

        self.assertIsInstance(widget, MyField)
        self.assertIs(widget.value, content)
        self.assertIs(widget.params, params)
        self.assertEqual(widget.name, 'field.test')

    def test_field_faile(self):
        from ptah import form

        field = form.FieldFactory(
            'new-field', 'test', title='Test field')

        self.assertRaises(
            TypeError, field.bind, '', object(), object())
