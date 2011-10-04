import colander
from memphis import form
from base import Base

node = colander.SchemaNode(
    colander.Str(),
    name = 'test',
    title = 'Test node')

node1 = colander.SchemaNode(
    colander.Str(),
    name = 'test1',
    title = 'Test node')


class TestField(Base):

    def test_field(self):
        from memphis.form.field import Field
        
        field = Field(node)
        
        self.assertEqual(field.name, 'test')
        self.assertFalse(field.readonly)
        self.assertEqual(repr(field), "<Field 'test'>")


class TestFieldset(Base):

    def test_fieldset_name_title(self):
        fieldset = form.Fieldset(node)
        
        self.assertEqual(fieldset.name, 'test')
        self.assertEqual(fieldset.legend, 'Test node')

        fieldset = form.Fieldset(node, name='othername', legend='Other name')
        
        self.assertEqual(fieldset.name, 'othername')
        self.assertEqual(fieldset.legend, 'Other name')

    def test_fieldset_append_simple(self):
        fieldset = form.Fieldset(node)

        self.assertIn('test', fieldset)
        self.assertIn('test.test', fieldset.names)
        self.assertEqual(fieldset.prefix, 'test.')

        self.assertIs(fieldset['test'].node, node)

        self.assertRaises(ValueError, fieldset.append, node)
        self.assertRaises(TypeError, fieldset.append, object())

    def test_fieldset_append_mapping(self):
        schema = colander.SchemaNode(
            colander.Mapping(),
            node,
            node1,
            name = 'schema')

        fieldset = form.Fieldset(schema)

        self.assertEqual(fieldset.prefix, 'schema.')
        self.assertEqual(fieldset.keys(), ['test', 'test1'])
        self.assertIn('test', fieldset)
        self.assertIn('test1', fieldset)

        fields = list(fieldset.fields())
        self.assertIs(fields[0].node, node)
        self.assertIs(fields[1].node, node1)
        
        self.assertRaises(ValueError, fieldset.append, schema)

    def test_fieldset_fiedset(self):
        schema = colander.SchemaNode(
            colander.Mapping(),
            node,
            node1,
            name = 'schema')

        fieldset = form.Fieldset(schema)
        self.assertEqual(list(fieldset.fieldsets()), [fieldset])

        schema = colander.SchemaNode(
            colander.Mapping(),
            colander.SchemaNode(
                colander.Mapping(),
                node,
                name = 'schema2'),
            name = 'schema',
            )

        fieldset.append(schema)
        self.assertEqual(len(list(fieldset.fieldsets())), 2)

        fs = fieldset['schema2']
        self.assertIsInstance(fs, form.Fieldset)
        self.assertIn('test', fs)
        
        self.assertRaises(ValueError, fieldset.append, schema)

    def test_fieldset_append_fieldset(self):
        schema = colander.SchemaNode(
            colander.Mapping(),
            node,
            name = 'schema')

        fieldset = form.Fieldset(schema)

        schema2 = colander.SchemaNode(
            colander.Mapping(),
            node1,
            name = 'schema2')

        fs = form.Fieldset(schema2)

        fieldset.append(fs)

        self.assertIn('schema.schema2', fieldset.names)
        self.assertIs(fieldset['schema2'], fs)
        self.assertRaises(ValueError, fieldset.append, fs)

    def test_fieldset_select(self):
        schema = colander.SchemaNode(
            colander.Mapping(),
            node,
            node1,
            name = 'schema')

        fieldset = form.Fieldset(schema)

        newfs = fieldset.select('test')
        self.assertNotIn('test1', newfs)
        self.assertEqual(newfs.keys(), ['test'])

    def test_fieldset_omit(self):
        schema = colander.SchemaNode(
            colander.Mapping(),
            node,
            node1,
            name = 'schema')

        fieldset = form.Fieldset(schema)

        newfs = fieldset.omit('test')
        self.assertNotIn('test', newfs)
        self.assertEqual(newfs.keys(), ['test1'])


class TestFields(Base):

    def test_fields(self):
        self.assertRaises(TypeError, form.Fields, object())
        
        class Schema(colander.Schema):

            test = colander.SchemaNode(
                colander.Str(),
                title = 'Test node')

        fields = form.Fieldset(Schema)
        self.assertEqual(fields.name, '')
        self.assertEqual(fields.prefix, '')
        self.assertIn('test', fields)
