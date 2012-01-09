import transaction
import sqlalchemy as sqla
from webob.multidict import MultiDict
from pyramid.testing import DummyRequest
from pyramid.compat import url_quote_plus
from pyramid.httpexceptions import HTTPFound
from pyramid.view import render_view_to_response

import ptah
from ptah.testing import PtahTestCase

Session = ptah.get_session()

class TestSqlaModuleTable(ptah.get_base()):

    __tablename__ = 'test_sqla_table'

    id = sqla.Column('id', sqla.Integer, primary_key=True)
    name = sqla.Column(sqla.Unicode(255))


class TestSqlaModule(PtahTestCase):

    def setUp(self):
        global TestSqlaModuleContent
        class TestSqlaModuleContent(ptah.cms.Content):
            __tablename__ = 'test_sqla_content'
            __table_args__ = {'extend_existing': True}
            __type__ = ptah.cms.Type('Test')
            name = sqla.Column(sqla.Unicode())

        #global TestSqlaModuleTable
        #class TestSqlaModuleTable(ptah.get_base()):
        #    __tablename__ = 'test_sqla_table'
        #    id = sqla.Column('id', sqla.Integer, primary_key=True)
        #    name = sqla.Column(sqla.Unicode(255))

        super(TestSqlaModule, self).setUp()

    def test_sqla_module(self):
        from ptah.manage.manage import PtahManageRoute
        from ptah.manage.sqla import SQLAModule, Table

        request = DummyRequest()

        cfg = ptah.get_settings(ptah.CFG_ID_PTAH, self.registry)
        cfg['managers'] = ['*']
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

        res = render_view_to_response(mod, request, '', False)
        self.assertEqual(res.status, '200 OK')

    def test_sqla_table_view(self):
        from ptah.manage.sqla import SQLAModule, TableView

        request = DummyRequest()

        mod = SQLAModule(None, request)
        table = mod['psqla-ptah_tokens']

        res = render_view_to_response(table, request, '', False)
        self.assertEqual(res.status, '200 OK')
        self.assertIn('form.buttons.add', res.text)

    def test_sqla_table_view_model(self):
        from ptah.manage.sqla import SQLAModule, TableView

        Session.add(TestSqlaModuleContent(title='test'))

        request = DummyRequest()

        mod = SQLAModule(None, request)
        table = mod['psqla-test_sqla_content']

        res = render_view_to_response(table, request, '', False).text
        self.assertIn('Inherits from:', res)
        self.assertIn('ptah_node', res)
        self.assertIn('ptah_content', res)
        self.assertNotIn('form.buttons.add', res)

    def test_sqla_table_view_model_nodes(self):
        from ptah.manage.sqla import SQLAModule, TableView

        rec = TestSqlaModuleContent(title='test')
        Session.add(rec)
        Session.flush()

        uri = rec.__uri__
        type_uri = rec.__type__.__uri__

        request = DummyRequest(params={'batch': 1})

        mod = SQLAModule(None, request)
        table = mod['psqla-ptah_nodes']

        res = render_view_to_response(table, request, '', False).text
        self.assertIn(url_quote_plus(uri), res)
        self.assertIn(url_quote_plus(type_uri), res)

        request = DummyRequest(params={'batch': 'unknown'})
        res = render_view_to_response(table, request, '', False).text
        self.assertIn(url_quote_plus(uri), res)

        request = DummyRequest(params={'batch': '0'})
        res = render_view_to_response(table, request, '', False).text
        self.assertIn(url_quote_plus(uri), res)

    def test_sqla_table_view_inheritance(self):
        from ptah.manage.sqla import SQLAModule, TableView

        request = DummyRequest()

        mod = SQLAModule(None, request)
        table = mod['psqla-ptah_tokens']

        res = render_view_to_response(table, request, '', False)
        self.assertEqual(res.status, '200 OK')

    def test_sqla_table_traverse(self):
        from ptah.manage.sqla import SQLAModule, Record
        from ptah.settings import SettingRecord

        inst = SettingRecord(name='test', value='12345')
        Session.add(inst)
        Session.flush()

        mod = SQLAModule(None, DummyRequest())
        table = mod['psqla-ptah_settings']

        rec = table[str(inst.name)]

        self.assertIsInstance(rec, Record)
        self.assertEqual(rec.pname, 'name')
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
        res = form.update()

        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], '.')

    def test_sqla_table_addrec_create(self):
        from ptah.manage.sqla import SQLAModule, AddRecord

        request = DummyRequest()

        mod = SQLAModule(None, request)
        table = mod['psqla-test_sqla_table']

        request = DummyRequest(
            POST={'form.buttons.create': 'Create'})

        form = AddRecord(table, request)
        form.csrf = False
        form.update()

        self.assertIn('Please fix indicated errors',
                      ptah.view.render_messages(request))

        request = DummyRequest(
            POST={'form.buttons.create': 'Create',
                  'name': 'Test'})

        form = AddRecord(table, request)
        form.csrf = False
        res = form.update()

        self.assertIn('Table record has been created.',
                      ptah.view.render_messages(request))
        self.assertIsInstance(res, HTTPFound)

        rec = Session.query(TestSqlaModuleTable).first()
        self.assertEqual(rec.name, 'Test')

    def test_sqla_table_addrec_create_multi(self):
        from ptah.manage.sqla import SQLAModule, AddRecord

        request = DummyRequest()

        mod = SQLAModule(None, request)
        table = mod['psqla-test_sqla_table']

        request = DummyRequest(
            POST={'form.buttons.createmulti': 'Create'})

        form = AddRecord(table, request)
        form.csrf = False
        form.update()

        self.assertIn('Please fix indicated errors',
                      ptah.view.render_messages(request))

        request = DummyRequest(
            POST={'form.buttons.createmulti': 'Create',
                  'name': 'Test multi'})

        form = AddRecord(table, request)
        form.csrf = False
        form.update()

        self.assertIn('Table record has been created.',
                      ptah.view.render_messages(request))

        rec = Session.query(TestSqlaModuleTable).first()
        self.assertEqual(rec.name, 'Test multi')

    def test_sqla_table_editrec_basics(self):
        from ptah.manage.sqla import SQLAModule, EditRecord

        rec = TestSqlaModuleTable()
        rec.name = 'Test record'
        Session.add(rec)
        Session.flush()

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
        res = form.update()

        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], '..')

    def test_sqla_table_editrec_modify(self):
        from ptah.manage.sqla import SQLAModule, EditRecord

        rec = TestSqlaModuleTable()
        rec.name = 'Test record'
        Session.add(rec)
        Session.flush()

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
                      ptah.view.render_messages(request))

        request = DummyRequest(
            POST={'form.buttons.modify': 'Modify',
                  'name': 'Record modified'})

        form = EditRecord(rec, request)
        form.csrf = False
        res = form.update()

        self.assertIn('Table record has been modified.',
                      ptah.view.render_messages(request))
        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], '..')

        rec = Session.query(TestSqlaModuleTable).filter(
            TestSqlaModuleTable.id == rec_id).first()
        self.assertEqual(rec.name, 'Record modified')

    def test_sqla_table_editrec_remove(self):
        from ptah.manage.sqla import SQLAModule, EditRecord

        rec = TestSqlaModuleTable()
        rec.name = 'Test record'
        Session.add(rec)
        Session.flush()

        rec_id = rec.id

        mod = SQLAModule(None, DummyRequest())
        table = mod['psqla-test_sqla_table']

        rec = table[rec_id]

        request = DummyRequest(
            POST={'form.buttons.remove': 'Remove'})

        form = EditRecord(rec, request)
        form.csrf = False
        res = form.update()

        self.assertIn('Table record has been removed.',
                      ptah.view.render_messages(request))
        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], '..')

        rec = Session.query(TestSqlaModuleTable).filter(
            TestSqlaModuleTable.id == rec_id).first()
        self.assertIsNone(rec, None)

    def test_sqla_table_add(self):
        from ptah.manage.sqla import SQLAModule, TableView

        mod = SQLAModule(None, DummyRequest())
        table = mod['psqla-test_sqla_table']

        request = DummyRequest(
            POST={'form.buttons.add': 'Add'})

        form = TableView(table, request)
        res = form.update()

        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], 'add.html')

    def test_sqla_table_remove(self):
        from ptah.manage.sqla import SQLAModule, TableView

        rec = TestSqlaModuleTable()
        rec.name = 'Test record'
        Session.add(rec)
        Session.flush()

        rec_id = rec.id

        mod = SQLAModule(None, DummyRequest())
        table = mod['psqla-test_sqla_table']

        request = DummyRequest(
            POST=MultiDict([('form.buttons.remove', 'Remove')]))

        form = TableView(table, request)
        form.csrf = False
        form.update()

        self.assertIn('lease select records for removing.',
                      ptah.view.render_messages(request))

        request = DummyRequest(
            POST=MultiDict([('form.buttons.remove', 'Remove'),
                            ('rowid', 'wrong')]))

        form = TableView(table, request)
        form.csrf = False
        form.update()

        #self.assertIn('Please select records for removing.',
        #              ptah.view.render_messages(request))

        request = DummyRequest(
            POST=MultiDict([('form.buttons.remove', 'Remove'),
                            ('rowid', rec_id),
                            ('csrf-token',
                             self.request.session.get_csrf_token())]))

        form = TableView(table, request)
        form.csrf = True
        form.update()

        self.assertIn('Select records have been removed.',
                      ptah.view.render_messages(request))

        rec = Session.query(TestSqlaModuleTable).filter(
            TestSqlaModuleTable.id == rec_id).first()
        self.assertIsNone(rec, None)

    def test_sqla_table_no_remove_for_edit_model(self):
        from ptah.manage.sqla import SQLAModule, EditRecord

        rec = TestSqlaModuleContent()
        rec.name = 'Test record'
        Session.add(rec)
        Session.flush()

        rec_id = rec.__id__

        mod = SQLAModule(None, DummyRequest())
        table = mod['psqla-test_sqla_content']

        rec = table[rec_id]

        form = EditRecord(rec, DummyRequest())
        form.update()

        self.assertNotIn('form.buttons.remove', form.render())
