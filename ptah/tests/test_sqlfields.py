import transaction
import sqlalchemy as sqla
import ptah
from ptah import form
from ptah.testing import PtahTestCase

Session = ptah.get_session()


class TestSqlSchema(PtahTestCase):

    def test_sqlschema_fields(self):
        import ptah

        class Test(ptah.get_base()):
            __tablename__ = 'test'

            id = sqla.Column('id', sqla.Integer, primary_key=True)
            name = sqla.Column(sqla.Unicode())
            count = sqla.Column(sqla.Integer())
            score = sqla.Column(sqla.Float())
            date = sqla.Column(sqla.Date())
            datetime = sqla.Column(sqla.DateTime())
            boolean = sqla.Column(sqla.Boolean())

        fieldset = ptah.generate_fieldset(Test)

        # no primary keya
        self.assertNotIn('id', fieldset)

        self.assertEqual(fieldset['name'].__field__, 'text')
        self.assertEqual(fieldset['count'].__field__, 'int')
        self.assertEqual(fieldset['score'].__field__, 'float')
        self.assertEqual(fieldset['date'].__field__, 'date')
        self.assertEqual(fieldset['datetime'].__field__, 'datetime')
        self.assertEqual(fieldset['boolean'].__field__, 'bool')
        self.assertEqual(fieldset['name'].title, 'Name')

        fieldset = ptah.generate_fieldset(Test, fieldNames=('name', 'count'))
        self.assertEqual(len(fieldset), 2)
        self.assertIn('name', fieldset)
        self.assertIn('count', fieldset)

        fieldset = ptah.generate_fieldset(
            Test, fieldNames=('id', 'name'), skipPrimaryKey=False)
        self.assertEqual(len(fieldset), 2)
        self.assertIn('name', fieldset)
        self.assertIn('id', fieldset)
        self.assertTrue(fieldset['id'].readonly)

        # no table
        class TestNoTable(Test):
            pass

        fieldset = ptah.generate_fieldset(TestNoTable)
        self.assertEqual(len(fieldset), 6)

    def test_sqlschema_extra_fields(self):
        import ptah

        class Test2(ptah.get_base()):
            __tablename__ = 'test2'

            id = sqla.Column('id', sqla.Integer, primary_key=True)
            name = sqla.Column(
                sqla.Unicode(),
                info={'title': 'Test title',
                      'missing': 'missing value',
                      'description': 'Description',
                      'field_type': 'textarea',
                      'vocabulary': ['1','2']})

        fieldset = ptah.generate_fieldset(Test2)

        field = fieldset['name']

        self.assertEqual(field.title, 'Test title')
        self.assertEqual(field.description, 'Description')
        self.assertEqual(field.missing, 'missing value')
        self.assertEqual(field.__field__, 'textarea')
        self.assertEqual(field.vocabulary, ['1', '2'])

    def test_sqlschema_custom(self):
        import ptah

        field = form.TextField('name', title = 'Custom')

        class Test3(ptah.get_base()):
            __tablename__ = 'test3'
            id = sqla.Column('id', sqla.Integer, primary_key=True)
            name = sqla.Column(sqla.Unicode(), info={'field': field})

        fieldset = ptah.generate_fieldset(Test3)

        m_field = fieldset['name']

        self.assertEqual(m_field.name, 'name')
        self.assertEqual(m_field.title, 'Custom')
        self.assertIs(m_field, field)

    def test_sqlschema_custom_type(self):
        import ptah

        class Test31(ptah.get_base()):
            __tablename__ = 'test31'
            id = sqla.Column('id', sqla.Integer, primary_key=True)
            name = sqla.Column(sqla.Unicode(), info={'field_type': 'int'})

        fieldset = ptah.generate_fieldset(Test31)

        m_field = fieldset['name']

        self.assertEqual(m_field.__field__, 'int')

    def test_sqlschema_custom_factory(self):
        import ptah

        class Test32(ptah.get_base()):
            __tablename__ = 'test32'
            id = sqla.Column('id', sqla.Integer, primary_key=True)
            name = sqla.Column(sqla.Unicode(),
                               info={'field_type': form.IntegerField})

        fieldset = ptah.generate_fieldset(Test32)

        m_field = fieldset['name']
        self.assertIsInstance(m_field, form.IntegerField)

    def test_sqlschema_skip(self):
        import ptah

        class Test34(ptah.get_base()):
            __tablename__ = 'test34'
            id = sqla.Column('id', sqla.Integer, primary_key=True)
            name = sqla.Column(sqla.Unicode(), info={'skip': True})

        fieldset = ptah.generate_fieldset(Test34)

        self.assertNotIn('name', fieldset)

    def test_sqlschema_unknown(self):
        import ptah

        class Test2(ptah.get_base()):
            __tablename__ = 'test5'

            id = sqla.Column('id', sqla.Integer, primary_key=True)
            name = sqla.Column(sqla.Unicode())
            json = sqla.Column(ptah.JsonListType())

        fieldset = ptah.generate_fieldset(Test2)

        self.assertNotIn('json', fieldset)


class TestQueryFreezer(PtahTestCase):

    _init_sqla = False

    def test_freezer_one(self):
        import ptah

        class Test(ptah.get_base()):
            __tablename__ = 'test10'

            id = sqla.Column('id', sqla.Integer, primary_key=True)
            name = sqla.Column(sqla.Unicode())

        ptah.get_base().metadata.create_all()
        transaction.commit()

        sql_get = ptah.QueryFreezer(
            lambda: Session.query(Test)
            .filter(Test.name == sqla.sql.bindparam('name')))

        self.assertRaises(
            sqla.orm.exc.NoResultFound, sql_get.one, name='test')

        rec = Test()
        rec.name = 'test'
        Session.add(rec)
        Session.flush()

        rec = sql_get.one(name='test')
        self.assertEqual(rec.name, 'test')

        rec = Test()
        rec.name = 'test'
        Session.add(rec)
        Session.flush()

        self.assertRaises(
            sqla.orm.exc.MultipleResultsFound, sql_get.one, name='test')

    def test_freezer_first(self):
        import ptah

        class Test(ptah.get_base()):
            __tablename__ = 'test12'

            id = sqla.Column('id', sqla.Integer, primary_key=True)
            name = sqla.Column(sqla.Unicode())

        ptah.get_base().metadata.create_all()
        transaction.commit()

        sql_get = ptah.QueryFreezer(
            lambda: Session.query(Test)
            .filter(Test.name == sqla.sql.bindparam('name')))

        self.assertIsNone(sql_get.first(name='test'))

        rec = Test()
        rec.name = 'test'
        Session.add(rec)
        Session.flush()

        rec = sql_get.one(name='test')
        self.assertEqual(rec.name, 'test')

        sql_get.reset()
        rec = sql_get.one(name='test')
        self.assertEqual(rec.name, 'test')


class TestJsonDict(PtahTestCase):

    _init_sqla = False

    def test_jsondict(self):
        import ptah
        ptah.reset_session()

        self.config.ptah_init_sql()

        class Test(ptah.get_base()):
            __tablename__ = 'test14'

            id = sqla.Column('id', sqla.Integer, primary_key=True)
            data = sqla.Column(ptah.JsonDictType())

        Session = ptah.get_session()
        ptah.get_base().metadata.create_all()
        transaction.commit()

        rec = Test()
        rec.data = {'test': 'val'}
        Session.add(rec)
        Session.flush()
        id = rec.id
        transaction.commit()

        rec = Session.query(Test).filter_by(id = id).one()
        self.assertEqual(rec.data, {'test': 'val'})

        rec.data['test2'] = 'val2'
        transaction.commit()

        rec = Session.query(Test).filter_by(id = id).one()
        self.assertEqual(rec.data,
                         {'test': 'val', 'test2': 'val2'})

        del rec.data['test']
        transaction.commit()

        rec = Session.query(Test).filter_by(id = id).one()
        self.assertEqual(rec.data, {'test2': 'val2'})


class TestJsonList(PtahTestCase):

    _init_sqla = False

    def test_jsonlist(self):
        import ptah

        Base = ptah.get_base()

        class Test(Base):
            __tablename__ = 'test15'

            id = sqla.Column('id', sqla.Integer, primary_key=True)
            data = sqla.Column(ptah.JsonListType())

        Session = ptah.get_session()
        Base.metadata.create_all()
        transaction.commit()

        rec = Test()
        rec.data = ['test']
        Session.add(rec)
        Session.flush()
        id = rec.id
        transaction.commit()

        rec = Session.query(Test).filter_by(id = id).one()
        self.assertEqual(rec.data, ['test'])

        rec.data[0] = 'test2'
        transaction.commit()

        rec = Session.query(Test).filter_by(id = id).one()
        self.assertEqual(rec.data, ['test2'])

        rec.data.append('test')
        transaction.commit()

        rec = Session.query(Test).filter_by(id = id).one()
        self.assertEqual(rec.data, ['test2', 'test'])

        del rec.data[rec.data.index('test2')]
        transaction.commit()

        rec = Session.query(Test).filter_by(id = id).one()
        self.assertEqual(rec.data, ['test'])
