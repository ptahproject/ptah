import transaction
import ptah
import sqlalchemy as sqla
from webob.multidict import MultiDict
from pyramid.testing import DummyRequest
from pyramid.httpexceptions import HTTPFound

from base import Base


class TestSqlaModuleContent(ptah.cms.Content):

    __tablename__ = 'test_sqla_content'
    __type__ = ptah.cms.Type('Test')
    name = sqla.Column(sqla.Unicode())


class TestSqlaModuleTable(ptah.cms.Base):

    __tablename__ = 'test_sqla_table'

    id = sqla.Column('id', sqla.Integer, primary_key=True)
    name = sqla.Column(sqla.Unicode())



class TestSqlaModule(Base):

    def tearDown(self):
        ptah.config.cleanup_system(self.__class__.__module__)
        super(TestSqlaModule, self).tearDown()

    def test_sqla_module(self):
        from ptah.manage.manage import CONFIG, PtahManageRoute
        from ptah.manage.sqla import SQLAModule, Table

        request = DummyRequest()

        CONFIG['managers'] = ['*']
        mr = PtahManageRoute(request)
        mod = mr['sqla']
        self.assertIsInstance(mod, SQLAModule)

        self.assertRaises(KeyError, mod.__getitem__, 'psqla-unknown')
        self.assertRaises(KeyError, mod.__getitem__, 'unknown')

        table = mod['psqla-ptah_tokens']
        self.assertIsInstance(table, Table)

    def test_sqla_traverse(self):
        from ptah.manage.sqla import SQLAModule, Table

        request = DummyRequest()

        mod = SQLAModule(None, request)

        table = mod['psqla-ptah_nodes']
        self.assertIsInstance(table, Table)

        self.assertRaises(KeyError, mod.__getitem__, 'unknown')

    def test_sqla_view(self):
        from ptah.manage.sqla import SQLAModule, MainView

        request = DummyRequest()

        mod = SQLAModule(None, request)

        res = MainView.__renderer__(mod, request)
        self.assertEqual(res.status, '200 OK')

    def test_sqla_table_view(self):
        from ptah.manage.sqla import SQLAModule, TableView

        request = DummyRequest()

        mod = SQLAModule(None, request)
        table = mod['psqla-ptah_tokens']

        res = TableView.__renderer__(table, request)
        self.assertEqual(res.status, '200 OK')
        self.assertIn('form.buttons.add', res.body)

    def test_sqla_table_view_model(self):
        from ptah.manage.sqla import SQLAModule, TableView

        ptah.cms.Session.add(TestSqlaModuleContent(title='test'))

        request = DummyRequest()

        mod = SQLAModule(None, request)
        table = mod['psqla-test_sqla_content']

        res = TableView.__renderer__(table, request).body
        self.assertIn('Inherits from:', res)
        self.assertIn('ptah_node', res)
        self.assertIn('ptah_content', res)
        self.assertNotIn('form.buttons.add', res)

    def test_sqla_table_view_model_nodes(self):
        from ptah.manage.sqla import SQLAModule, TableView

        rec = TestSqlaModuleContent(title='test')
        ptah.cms.Session.add(rec)
        ptah.cms.Session.flush()

        uri = rec.__uri__
        type_uri = rec.__type__.__uri__

        request = DummyRequest(params={'batch': 1})

        mod = SQLAModule(None, request)
        table = mod['psqla-ptah_nodes']

        res = TableView.__renderer__(table, request).body
        self.assertIn(uri, res)
        self.assertIn(type_uri, res)

        request = DummyRequest(params={'batch': 'unknown'})
        res = TableView.__renderer__(table, request).body
        self.assertIn(uri, res)

        request = DummyRequest(params={'batch': '0'})
        res = TableView.__renderer__(table, request).body
        self.assertIn(uri, res)

    def test_sqla_table_view_inheritance(self):
        from ptah.manage.sqla import SQLAModule, TableView

        request = DummyRequest()

        mod = SQLAModule(None, request)
        table = mod['psqla-ptah_tokens']

        res = TableView.__renderer__(table, request)
        self.assertEqual(res.status, '200 OK')

    def test_sqla_table_traverse(self):
        from ptah.manage.sqla import SQLAModule, Record

        from ptah import token
        from ptah.util import CSRFService

        tid = token.service.generate(CSRFService.TOKEN_TYPE, 'test')
        inst = token.service._sql_get.first(token=tid)

        request = DummyRequest()

        mod = SQLAModule(None, request)
        table = mod['psqla-ptah_tokens']

        rec = table[str(inst.id)]

        self.assertIsInstance(rec, Record)
        self.assertEqual(rec.pname, 'id')
        self.assertIsNotNone(rec.pcolumn)
        self.assertIsNotNone(rec.data)

        self.assertRaises(KeyError, table.__getitem__, 'add.html')
        self.assertRaises(KeyError, table.__getitem__, 'unknown')

    def test_sqla_table_addrec_basics(self):
        from ptah.manage.sqla import SQLAModule, AddRecord

        request = DummyRequest()

        mod = SQLAModule(None, request)
        table = mod['psqla-test_sqla_table']

        form = AddRecord(table, request)
        form.update()

        self.assertEqual(form.label, 'test_sqla_table: new record')

        request = DummyRequest(
            POST={'form.buttons.back': 'Back'})

        form = AddRecord(table, request)
        try:
            form.update()
        except Exception, res:
            pass

        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], '.')

    def test_sqla_table_addrec_create(self):
        from ptah.manage.sqla import SQLAModule, AddRecord

        request = DummyRequest()

        mod = SQLAModule(None, request)
        table = mod['psqla-test_sqla_table']

        request = DummyRequest(
            session = {},
            POST={'form.buttons.create': 'Create'})

        form = AddRecord(table, request)
        form.csrf = False
        form.update()

        self.assertIn('Please fix indicated errors',
                      request.session['msgservice'][0])

        request = DummyRequest(
            session = {},
            POST={'form.buttons.create': 'Create',
                  'name': 'Test'})

        form = AddRecord(table, request)
        form.csrf = False
        try:
            form.update()
        except Exception, res:
            pass

        self.assertIn('Table record has been created.',
                      request.session['msgservice'][0])
        self.assertIsInstance(res, HTTPFound)

        rec = ptah.cms.Session.query(TestSqlaModuleTable).first()
        self.assertEqual(rec.name, 'Test')

    def test_sqla_table_addrec_create_multi(self):
        from ptah.manage.sqla import SQLAModule, AddRecord

        request = DummyRequest()

        mod = SQLAModule(None, request)
        table = mod['psqla-test_sqla_table']

        request = DummyRequest(
            session = {},
            POST={'form.buttons.createmulti': 'Create'})

        form = AddRecord(table, request)
        form.csrf = False
        form.update()

        self.assertIn('Please fix indicated errors',
                      request.session['msgservice'][0])

        request = DummyRequest(
            session = {},
            POST={'form.buttons.createmulti': 'Create',
                  'name': 'Test multi'})

        form = AddRecord(table, request)
        form.csrf = False
        form.update()

        self.assertIn('Table record has been created.',
                      request.session['msgservice'][0])

        rec = ptah.cms.Session.query(TestSqlaModuleTable).first()
        self.assertEqual(rec.name, 'Test multi')

    def test_sqla_table_editrec_basics(self):
        from ptah.manage.sqla import SQLAModule, EditRecord

        rec = TestSqlaModuleTable()
        rec.name = 'Test record'
        ptah.cms.Session.add(rec)
        ptah.cms.Session.flush()

        rec_id = rec.id

        request = DummyRequest()

        mod = SQLAModule(None, request)
        table = mod['psqla-test_sqla_table']

        rec = table[rec_id]

        form = EditRecord(rec, request)
        form.update()

        self.assertEqual(form.label, 'record 1')
        self.assertEqual(form.form_content(),
                         {'name': 'Test record'})

        request = DummyRequest(
            POST={'form.buttons.cancel': 'Cancel'})

        form = EditRecord(rec, request)
        try:
            form.update()
        except Exception, res:
            pass

        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], '..')

    def test_sqla_table_editrec_modify(self):
        from ptah.manage.sqla import SQLAModule, EditRecord

        rec = TestSqlaModuleTable()
        rec.name = 'Test record'
        ptah.cms.Session.add(rec)
        ptah.cms.Session.flush()

        rec_id = rec.id

        mod = SQLAModule(None, DummyRequest())
        table = mod['psqla-test_sqla_table']

        rec = table[rec_id]

        request = DummyRequest(
            POST={'form.buttons.modify': 'Modify'})

        form = EditRecord(rec, request)
        form.csrf = False
        form.update()

        self.assertIn('Please fix indicated errors',
                      request.session['msgservice'][0])

        request = DummyRequest(
            session = {},
            POST={'form.buttons.modify': 'Modify',
                  'name': 'Record modified'})

        form = EditRecord(rec, request)
        form.csrf = False
        try:
            form.update()
        except Exception, res:
            pass

        self.assertIn('Table record has been modified.',
                      request.session['msgservice'][0])
        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], '..')

        rec = ptah.cms.Session.query(TestSqlaModuleTable).filter(
            TestSqlaModuleTable.id == rec_id).first()
        self.assertEqual(rec.name, 'Record modified')

    def test_sqla_table_editrec_remove(self):
        from ptah.manage.sqla import SQLAModule, EditRecord

        rec = TestSqlaModuleTable()
        rec.name = 'Test record'
        ptah.cms.Session.add(rec)
        ptah.cms.Session.flush()

        rec_id = rec.id

        mod = SQLAModule(None, DummyRequest())
        table = mod['psqla-test_sqla_table']

        rec = table[rec_id]

        request = DummyRequest(
            POST={'form.buttons.remove': 'Remove'})

        form = EditRecord(rec, request)
        form.csrf = False
        try:
            form.update()
        except Exception, res:
            pass

        self.assertIn('Table record has been removed.',
                      request.session['msgservice'][0])
        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], '..')

        rec = ptah.cms.Session.query(TestSqlaModuleTable).filter(
            TestSqlaModuleTable.id == rec_id).first()
        self.assertIsNone(rec, None)

    def test_sqla_table_add(self):
        from ptah.manage.sqla import SQLAModule, TableView

        mod = SQLAModule(None, DummyRequest())
        table = mod['psqla-test_sqla_table']

        request = DummyRequest(
            POST={'form.buttons.add': 'Add'})

        form = TableView(table, request)
        try:
            form.update()
        except Exception, res:
            pass

        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], 'add.html')

    def test_sqla_table_remove(self):
        from ptah.manage.sqla import SQLAModule, TableView

        rec = TestSqlaModuleTable()
        rec.name = 'Test record'
        ptah.cms.Session.add(rec)
        ptah.cms.Session.flush()

        rec_id = rec.id

        mod = SQLAModule(None, DummyRequest())
        table = mod['psqla-test_sqla_table']

        request = DummyRequest(
            POST=MultiDict({'form.buttons.remove': 'Remove'}))

        form = TableView(table, request)
        form.csrf = False
        form.update()

        self.assertIn('lease select records for removing.',
                      request.session['msgservice'][0])

        request = DummyRequest(
            POST=MultiDict({'form.buttons.remove': 'Remove',
                            'rowid': 'wrong'}))

        form = TableView(table, request)
        form.csrf = False
        form.update()

        self.assertIn('lease select records for removing.',
                      request.session['msgservice'][0])

        request = DummyRequest(
            POST=MultiDict({'form.buttons.remove': 'Remove',
                            'rowid': rec_id}))

        form = TableView(table, request)
        form.csrf = False
        form.update()

        self.assertIn('Select records have been removed.',
                      request.session['msgservice'][0])

        rec = ptah.cms.Session.query(TestSqlaModuleTable).filter(
            TestSqlaModuleTable.id == rec_id).first()
        self.assertIsNone(rec, None)

    def test_sqla_table_no_remove_for_edit_model(self):
        from ptah.manage.sqla import SQLAModule, EditRecord

        rec = TestSqlaModuleContent()
        rec.name = 'Test record'
        ptah.cms.Session.add(rec)
        ptah.cms.Session.flush()

        rec_id = rec.__id__

        mod = SQLAModule(None, DummyRequest())
        table = mod['psqla-test_sqla_content']

        rec = table[rec_id]

        form = EditRecord(rec, DummyRequest())
        form.update()

        self.assertNotIn('form.buttons.remove', form.render())
