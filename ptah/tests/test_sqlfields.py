import colander
import sqlalchemy as sqla
from zope import interface
from memphis import config

from base import Base


class TestSqlSchema(Base):

    def test_sqlschema_fields(self):
        import ptah_cms
        from ptah_cms.sqlschema import generateSchema

        # no table
        class TestNoTable(ptah_cms.Node):
            pass
            
        self.assertIsNone(generateSchema(TestNoTable))

        class Test(ptah_cms.Base):
            __tablename__ = 'test'
            
            id = sqla.Column('id', sqla.Integer, primary_key=True)
            name = sqla.Column(sqla.Unicode())
            count = sqla.Column(sqla.Integer())
            score = sqla.Column(sqla.Float())
            date = sqla.Column(sqla.Date())
            datetime = sqla.Column(sqla.DateTime())
            boolean = sqla.Column(sqla.Boolean())

        schema = generateSchema(Test)

        # no primary keya
        self.assertNotIn('id', schema)

        self.assertIsInstance(schema['name'].typ, colander.Str)
        self.assertIsInstance(schema['count'].typ, colander.Int)
        self.assertIsInstance(schema['score'].typ, colander.Float)
        self.assertIsInstance(schema['date'].typ, colander.Date)
        self.assertIsInstance(schema['datetime'].typ, colander.DateTime)
        self.assertIsInstance(schema['boolean'].typ, colander.Bool)

        self.assertEqual(schema['name'].title, 'Name')


        schema = generateSchema(Test, schemaNodes=('name', 'count'))
        self.assertEqual(len(schema.children), 2)
        self.assertIn('name', schema)
        self.assertIn('count', schema)

        schema = generateSchema(
            Test, schemaNodes=('id', 'name'), skipPrimaryKey=False)
        self.assertEqual(len(schema.children), 2)
        self.assertIn('name', schema)
        self.assertIn('id', schema)
        self.assertTrue(schema['id'].readonly)

    def test_sqlschema_extra_fields(self):
        import ptah_cms
        from ptah_cms.sqlschema import generateSchema

        class Test2(ptah_cms.Base):
            __tablename__ = 'test2'

            id = sqla.Column('id', sqla.Integer, primary_key=True)
            name = sqla.Column(
                sqla.Unicode(),
                info={'title': 'Test title',
                      'missing': 'missing value',
                      'description': 'Description',
                      'widget': 'textarea',
                      'vocabulary': ['1','2']})

        schema = generateSchema(Test2)

        node = schema['name']
        
        self.assertEqual(node.title, 'Test title')
        self.assertEqual(node.description, 'Description')
        self.assertEqual(node.missing, 'missing value')
        self.assertEqual(node.widget, 'textarea')
        self.assertEqual(node.vocabulary, ['1', '2'])

    def test_sqlschema_custom(self):
        import ptah_cms
        from ptah_cms.sqlschema import generateSchema

        node = colander.SchemaNode(
            colander.Str(),
            title = 'Custom')

        class Test3(ptah_cms.Base):
            __tablename__ = 'test3'
            id = sqla.Column('id', sqla.Integer, primary_key=True)
            name = sqla.Column(sqla.Unicode(), info={'node': node})

        schema = generateSchema(Test3)

        m_node = schema['name']

        self.assertEqual(m_node.name, 'name')        
        self.assertEqual(m_node.title, 'Custom')
        self.assertIs(m_node, node)
