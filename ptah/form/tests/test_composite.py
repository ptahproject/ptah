from unittest import mock
import ptah.form
from ptah.testing import TestCase, BaseTestCase


class TestCompositeError(TestCase):
    """ Tests for ptah.form.CompositeError """

    def test_type(self):
        self.assertTrue(
            issubclass(ptah.form.CompositeError, ptah.form.Invalid))

    def test_repr(self):
        err = ptah.form.CompositeError('test')
        self.assertIn('CompositeError<: test>:\n{', repr(err))


class TestCompositeField(BaseTestCase):
    """ Tests for ptah.form.CompositeField """

    _includes = ['ptah.form']

    def test_ctor(self):
        """ Composite field requires fields """
        self.assertRaises(
            ValueError, ptah.form.CompositeField, 'test')

    def test_ctor_fields(self):
        """ Composite field converts sequence of fields to Fieldset """
        field = ptah.form.CompositeField(
            'test', fields=(ptah.form.TextField('firstname'),
                            ptah.form.TextField('lastname')))
        self.assertIsInstance(field.fields, ptah.form.Fieldset)

    def test_default(self):
        """ Default composite field value """
        field = ptah.form.CompositeField(
            'test', fields=(ptah.form.TextField('firstname'),
                            ptah.form.TextField('lastname')))
        self.assertEqual(
            {'lastname': '', 'firstname': ''}, field.default)

    def test_default_from_fields(self):
        """ Set default composite field value """
        field = ptah.form.CompositeField(
            'test',
            fields=(ptah.form.TextField('firstname',default='1'),
                    ptah.form.TextField('lastname', default='2')))
        self.assertEqual(
            {'lastname': '2', 'firstname': '1'}, field.default)

    def test_set_default(self):
        """ Set default composite field value """
        field = ptah.form.CompositeField(
            'test',
            default={'firstname': '123'},
            fields=(ptah.form.TextField('firstname'),
                    ptah.form.TextField('lastname')))
        self.assertEqual(
            {'firstname': '123'}, field.default)

    def test_ctor_fields_prefix(self):
        """ Composite field uses custom fields prefix """
        field = ptah.form.CompositeField(
            'test', fields=ptah.form.Fieldset(
                ptah.form.TextField('firstname'),
                ptah.form.TextField('lastname'),
                name = 'fieldset'))

        self.assertEqual('test.', field.fields.prefix)

    def test_bind(self):
        """ Composite field convert null value into dictionary """
        field = ptah.form.CompositeField(
            'test', fields=(ptah.form.TextField('firstname'),))

        widget = field.bind(self.request, '', ptah.form.null, {})
        self.assertEqual({}, widget.value)

        widget = field.bind(self.request, '', None, {})
        self.assertEqual({}, widget.value)

        self.assertEqual(ptah.form.null, widget.fields['firstname'].value)

        self.assertEqual('test', widget.name)
        self.assertEqual('test.firstname', widget.fields['firstname'].name)

    def test_bind_fields(self):
        """ Composite field bind fields as well """
        field = ptah.form.CompositeField(
            'test', fields=(ptah.form.TextField('firstname'),))

        widget = field.bind(self.request, '', {'firstname': 'Nikolay'}, {})
        self.assertEqual('Nikolay', widget.fields['firstname'].value)

    def test_bind_flat_fields(self):
        """ Composite field bind flat fields """
        field = ptah.form.CompositeField(
            'test', fields=(
                ptah.form.CompositeField(
                    'sub', flat=True, fields=(ptah.form.TextField('firstname'),)),
                ptah.form.TextField('lastname')))

        widget = field.bind(self.request, '',
                            {'firstname': 'Nikolay', 'lastname': 'Kim'}, {})
        self.assertEqual(
            'Nikolay', widget.fields['sub'].fields['firstname'].value)

    def test_set_id_prefix(self):
        """ Composite field sets id for subfields """
        field = ptah.form.CompositeField(
            'test', fields=(ptah.form.TextField('firstname'),))

        field.set_id_prefix('prefix.')
        self.assertEqual('prefix-test', field.id)
        self.assertEqual('prefix-test-firstname', field.fields['firstname'].id)

    def test_extract(self):
        """ Extract form data """
        field = ptah.form.CompositeField(
            'test', fields=(ptah.form.TextField('firstname'),
                            ptah.form.TextField('lastname')))

        widget = field.bind(self.request, '', None,
                            {'test.lastname': ptah.form.null,
                             'test.firstname':'Nikolay'})
        result = widget.extract()
        self.assertEqual({'lastname': '', 'firstname': 'Nikolay'}, result)

    def test_extract_missing(self):
        """ Extract returns missing """
        fields=(ptah.form.TextField('firstname', missing='name'),
                ptah.form.TextField('lastname'))

        field = ptah.form.CompositeField('test', fields=fields)

        widget = field.bind(self.request, '', None, {})

        result = widget.extract()
        self.assertEqual({'lastname': fields[1].missing,
                          'firstname': fields[0].missing}, result)

    def test_form_extract_missing(self):
        """ Extract form data, composite field no data """
        fields=(ptah.form.TextField('firstname', missing='name'),
                ptah.form.TextField('lastname'))

        field = ptah.form.CompositeField('test', fields=fields)

        form = ptah.form.Form(object(), self.request, fields=(field,))
        form.update_form()

        data, errors = form.extract()
        self.assertEqual({'lastname': fields[1].missing,
                          'firstname': fields[0].missing}, data['test'])

    def test_validate(self):
        """ Validate data """
        field = ptah.form.CompositeField(
            'test', fields=(ptah.form.TextField('firstname'),
                            ptah.form.TextField('lastname')))

        with self.assertRaises(ptah.form.Invalid) as cm:
            field.validate({'lastname':'', 'firstname': 'Nikolay'})

        err = cm.exception
        self.assertEqual(1, len(err.errors))
        self.assertIn('lastname', err)

    def test_validate_consolidate_errs(self):
        """ Validate data (consolidate_errors) """
        field = ptah.form.CompositeField(
            'test',
            consolidate_errors=True,
            fields=(ptah.form.TextField('firstname'),
                    ptah.form.TextField('lastname')))

        with self.assertRaises(ptah.form.Invalid) as cm:
            field.validate({'lastname':'', 'firstname': 'Nikolay'})

        err = cm.exception
        self.assertEqual(0, len(err.errors))
        self.assertIn('Required', err.msg)

    def test_custom_validator(self):
        """ Custom validator """
        v = mock.Mock()
        field = ptah.form.CompositeField(
            'test', fields=(ptah.form.TextField('firstname'),
                            ptah.form.TextField('lastname')),
            validator=v
        )
        field.validate({'lastname':'Kim', 'firstname': 'Nikolay'})
        self.assertIs(v.call_args[0][0], field)

    def test_to_field_exception(self):
        """ Composite field, convert form data to field data with error """
        field = ptah.form.CompositeField(
            'test', fields=(ptah.form.TextField('name'),
                            ptah.form.IntegerField('age')))

        with self.assertRaises(ptah.form.Invalid) as cm:
            field.to_field({'name': 'Nikolay', 'age': 'www'})

        self.assertIn('age', cm.exception)

    def test_to_field_exception_consolidate_errs(self):
        """ Composite field, convert form data to field data with error (consolidate) """
        field = ptah.form.CompositeField(
            'test',
            consolidate_errors = True,
            fields=(ptah.form.TextField('name'),
                    ptah.form.IntegerField('age')))

        with self.assertRaises(ptah.form.Invalid) as cm:
            field.to_field({'name': 'Nikolay', 'age': 'www'})

        self.assertNotIn('age', cm.exception)
        self.assertEqual('"${val}" is not a number', cm.exception.msg)

    def test_to_field(self):
        """ Composite field, convert form data to field data """
        field = ptah.form.CompositeField(
            'test', fields=(ptah.form.TextField('name'),
                            ptah.form.IntegerField('age')))

        result = field.to_field({'name': 'Nikolay', 'age': '123'})
        self.assertEqual({'name':'Nikolay', 'age':123}, result)

    def test_update(self):
        """ Composite field, update subfields """
        field = ptah.form.CompositeField('test', fields=(ptah.form.TextField('name'),))

        widget = field.bind(self.request, '', None,
                            {'test.name': 'Nikolay'})
        widget.update()

        self.assertEqual('Nikolay', widget.fields['name'].form_value)

    def test_flatten(self):
        """ Composite field, flatten """
        field = ptah.form.CompositeField(
            'test', fields=(ptah.form.TextField('name'),
                            ptah.form.TextField('age'),))

        self.assertEqual({'name':'n', 'age': '123'},
                         field.flatten({'name':'n', 'age': '123'}))

        self.assertEqual({'name':'n', 'age': '123', 'extra':'1'},
                         field.flatten({'name':'n', 'age': '123','extra':'1'}))

    def test_flatten_recursive(self):
        """ Composite field, recursive flatten """
        field = ptah.form.CompositeField(
            'test', fields=(
                ptah.form.TextField('name'),
                ptah.form.CompositeField(
                    'address', flat=True,
                    fields=(ptah.form.TextField('street'),))))

        self.assertEqual(
            field.flatten({'name':'n', 'address': {'street':'123'}}),
            {'name':'n', 'street': '123'})

    def test_render_widget(self):
        """ Composite field render widget """
        field = ptah.form.CompositeField(
            'test', title='Test', fields=(ptah.form.TextField('name'),))

        widget = field.bind(self.request, '', None,
                            {'test.name': 'Nikolay'})
        widget.update()

        res = widget.render_widget()
        self.assertIn(
            '<label class="control-label">Test', res)
        self.assertIn(
            '<input type="text" class="form-control text-widget" value="Nikolay"', res)

    def test_render_widget_with_error(self):
        """ Composite field render widget with error """
        field = ptah.form.CompositeField('test', fields=(ptah.form.TextField('name'),))

        widget = field.bind(self.request, '', None, {})
        widget.update()
        self.assertRaises(ptah.form.Invalid, widget.validate, {'name': ''})

        res = widget.render_widget()
        self.assertIn('<div class="control-group error">', res)
        self.assertIn('<span class="help-inline">Required</span>', res)

    def test_render(self):
        """ Composite field render """
        field = ptah.form.CompositeField(
            'test', fields=(ptah.form.TextField('name', title='Name'),))

        widget = field.bind(self.request, '', None,
                            {'test.name': 'Nikolay'})
        widget.update()

        res = widget.render()
        self.assertIn(
            '<input type="text" class="form-control text-widget" value="Nikolay" id="test-test-name" name="test.name" title="Name">', res)
