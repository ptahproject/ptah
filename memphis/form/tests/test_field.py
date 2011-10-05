from memphis import form
from base import Base

field = form.TextField(
    'test', title = 'Test node')

field1 = form.TextField(
    'test1', title = 'Test node')


class TestFieldset(Base):

    def test_fieldset_name_title(self):
        fieldset = form.Fieldset(field)

        self.assertEqual(fieldset.name, '')
        self.assertEqual(fieldset.legend, '')

        fieldset = form.Fieldset(field1, name='othername', legend='Other name')

        self.assertEqual(fieldset.name, 'othername')
        self.assertEqual(fieldset.legend, 'Other name')

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
        self.assertEqual(newfs.keys(), ['test'])

    def test_fieldset_omit(self):
        fieldset = form.Fieldset(field, field1)

        newfs = fieldset.omit('test')
        self.assertNotIn('test', newfs)
        self.assertEqual(newfs.keys(), ['test1'])

    def test_fieldset_add(self):
        fieldset = form.Fieldset(field)
        fieldset = fieldset + form.Fieldset(field1)

        self.assertIn('test', fieldset)
        self.assertIn('test1', fieldset)
        self.assertEqual(fieldset.keys(), ['test', 'test1'])

    def test_fieldset_iadd(self):
        fieldset = form.Fieldset(field)
        fieldset += form.Fieldset(field1)

        self.assertIn('test', fieldset)
        self.assertIn('test1', fieldset)
        self.assertEqual(fieldset.keys(), ['test', 'test1'])

    def test_fieldset_add_err(self):
        fieldset = form.Fieldset(field)

        self.assertRaises(ValueError, fieldset.__add__, object())

