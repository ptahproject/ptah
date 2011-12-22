import sqlalchemy as sqla
import transaction
import ptah
from ptah import cms
from ptah.testing import PtahTestCase
from webob.multidict import MultiDict
from pyramid.testing import DummyRequest
from pyramid.httpexceptions import HTTPFound
from pyramid.view import render_view_to_response


class Base(PtahTestCase):

    def setUp(self):
        global Content1, Content2
        class Content1(cms.Content):
            __type__ = cms.Type('content1')

        class Content2(cms.Node):
            __tablename__ = 'test_model_base'
            __table_args__ = {'extend_existing': True}
            __id__ = sqla.Column(
                'id', sqla.Integer,
                sqla.ForeignKey('ptah_nodes.id'), primary_key=True)

            __type__ = cms.Type('content2')

            title = sqla.Column(sqla.Unicode, default='')

        self.Content1 = Content1
        self.Content2 = Content2

        super(Base, self).setUp()


class TestModelModule(Base):

    def test_model_module(self):
        from ptah.manage.model import ModelModule
        from ptah.manage.manage import PtahManageRoute

        request = DummyRequest()

        ptah.auth_service.set_userid('test')
        cfg = ptah.get_settings(ptah.CFG_ID_PTAH, self.registry)
        cfg['managers'] = ('*',)
        mr = PtahManageRoute(request)
        mod = mr['models']

        self.assertIsInstance(mod, ModelModule)

    def test_model_view(self):
        from ptah.manage.model import ModelModule, ModelModuleView

        request = DummyRequest()

        mod = ModelModule(None, request)

        res = render_view_to_response(mod, request, '', False)
        self.assertEqual(res.status, '200 OK')
        self.assertIn('content1', res.text)
        self.assertIn('content2', res.text)

    def test_model_view_disabled(self):
        from ptah.manage.model import ModelModule, ModelModuleView

        cfg = ptah.get_settings(ptah.CFG_ID_PTAH, self.registry)
        cfg['disable_models'] = ['cms-type:content2']

        request = DummyRequest()

        mod = ModelModule(None, request)

        res = render_view_to_response(mod, request, '', False)
        self.assertEqual(res.status, '200 OK')
        self.assertIn('content1', res.text)
        self.assertNotIn('content2', res.text)

    def test_model_traverse(self):
        from ptah.manage.model import ModelModule, Model

        request = DummyRequest()

        mod = ModelModule(None, request)

        item = mod['content1']
        self.assertIsInstance(item, Model)
        self.assertIs(item.tinfo, Content1.__type__)

        item = mod['content2']
        self.assertIsInstance(item, Model)
        self.assertIs(item.tinfo, Content2.__type__)

        self.assertRaises(KeyError, mod.__getitem__, 'unknown')


class TestModel(Base):

    def test_model_traverse(self):
        from ptah.manage.model import ModelModule, Record

        content = Content1()
        content.title = 'Content test'

        Session = ptah.get_session()
        Session.add(content)
        Session.flush()

        rowid = content.__id__
        transaction.commit()

        mod = ModelModule(None, DummyRequest())
        model = mod['content1']

        rec = model[str(rowid)]
        self.assertIsNotNone(rec)
        self.assertIsInstance(rec, Record)
        self.assertIsInstance(rec.record, Content1)
        self.assertEqual(rec.record.__id__, rowid)
        self.assertRaises(KeyError, model.__getitem__, 'add.html')
        self.assertRaises(KeyError, model.__getitem__, 'unknown')

    def test_model_remove_errors(self):
        from ptah.manage.model import ModelModule, ModelView

        mod = ModelModule(None, DummyRequest())
        model = mod['content1']

        form = ModelView(
            model, DummyRequest(
                POST=MultiDict([('form.buttons.remove', 'Remove')])))
        form.csrf = False
        form.update()

        self.assertIn("Please select records for removing.",
                      ptah.view.render_messages(form.request))

    def test_model_remove(self):
        from ptah.manage.model import ModelModule, ModelView

        content = Content1()
        content.title = 'Content test'

        Session = ptah.get_session()
        Session.add(content)
        Session.flush()

        rowid = content.__id__
        transaction.commit()

        mod = ModelModule(None, DummyRequest())
        model = mod['content1']

        form = ModelView(
            model, DummyRequest(
                POST=MultiDict(
                    list({'rowid':rowid,
                          'form.buttons.remove': 'Remove'}.items()))))
        form.csrf = False
        res = form.update()

        self.assertIsInstance(res, HTTPFound)

        transaction.commit()

        Session = ptah.get_session()
        rec = Session.query(Content1).filter(
            Content1.__id__ == rowid).first()
        self.assertIsNone(rec)

    def test_model_list(self):
        from ptah.manage.model import ModelModule, ModelView

        content = Content1()
        content.title = 'Content test'

        Session = ptah.get_session()
        Session.add(content)
        Session.flush()

        rowid = content.__id__
        transaction.commit()

        mod = ModelModule(None, DummyRequest())
        model = mod['content1']

        res = render_view_to_response(model, DummyRequest(), '', False)
        self.assertIn('value="%s"'%rowid, res.text)

        res = render_view_to_response(
            model, DummyRequest(params={'batch': 0}), '', False)
        self.assertIn('value="%s"'%rowid, res.text)

        res = render_view_to_response(
            model, DummyRequest(params={'batch': 'unknown'}), '', False)
        self.assertIn('value="%s"'%rowid, res.text)

    def test_model_add(self):
        from ptah.manage.model import ModelModule, ModelView

        mod = ModelModule(None, DummyRequest())
        model = mod['content1']

        form = ModelView(
            model, DummyRequest(POST={'form.buttons.add': 'Add'}))
        form.csrf = False
        res = form.update()

        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], 'add.html')


class TestAddRecord(Base):

    def test_model_add_errors(self):
        from ptah.manage.model import ModelModule, AddRecord

        mod = ModelModule(None, DummyRequest())
        model = mod['content1']

        form = AddRecord(
            model, DummyRequest(POST={'form.buttons.add': 'Add'}))
        form.csrf = False
        form.update()

        self.assertIn("Please fix indicated errors.",
                      ptah.view.render_messages(form.request))

    def test_model_add_back(self):
        from ptah.manage.model import ModelModule, AddRecord

        mod = ModelModule(None, DummyRequest())
        model = mod['content1']

        form = AddRecord(
            model, DummyRequest(POST={'form.buttons.back': 'Back'}))
        form.csrf = False
        res = form.update()

        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], '.')

    def test_model_add(self):
        from ptah.manage.model import ModelModule, AddRecord

        mod = ModelModule(None, DummyRequest())
        model = mod['content1']

        form = AddRecord(
            model, DummyRequest(
                POST={'title': 'Test content',
                      'form.buttons.add': 'Add'}))
        form.csrf = False
        res = form.update()

        id = form.record.__id__
        transaction.commit()

        Session = ptah.get_session()
        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], './%s/'%id)
        self.assertEqual(len(Session.query(self.Content1).all()), 1)

        content = Session.query(self.Content1) \
            .filter(self.Content1.__id__ == id).first()
        self.assertEqual(content.title, 'Test content')

    def test_model_add_node(self):
        from ptah.manage.model import ModelModule, AddRecord

        mod = ModelModule(None, DummyRequest())
        model = mod['content2']

        form = AddRecord(
            model, DummyRequest(
                POST={'title': 'Test content', 'form.buttons.add': 'Add'}))
        form.csrf = False
        res = form.update()

        id = form.record.__id__
        transaction.commit()

        Session = ptah.get_session()
        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], './%s/'%id)
        self.assertEqual(len(Session.query(self.Content2).all()), 1)

        content = Session.query(self.Content2) \
            .filter(self.Content2.__id__ == id).first()
        self.assertEqual(content.title, 'Test content')


class TestEditRecord(Base):

    def test_model_edit_back(self):
        from ptah.manage.model import ModelModule, EditRecord

        content = Content1()
        content.title = 'Content test'

        Session = ptah.get_session()
        Session.add(content)
        Session.flush()

        rowid = content.__id__
        transaction.commit()

        mod = ModelModule(None, DummyRequest())
        model = mod['content1'][rowid]

        form = EditRecord(
            model, DummyRequest(POST={'form.buttons.back': 'Back'}))
        form.csrf = False
        res = form.update()

        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], '../')

    def test_model_edit_errors(self):
        from ptah.manage.model import ModelModule, EditRecord

        content = Content1()
        content.title = 'Content test'

        Session = ptah.get_session()
        Session.add(content)
        Session.flush()

        rowid = content.__id__
        transaction.commit()

        mod = ModelModule(None, DummyRequest())
        model = mod['content1'][rowid]

        form = EditRecord(
            model, DummyRequest(POST={'form.buttons.modify': 'Modify'}))
        form.csrf = False
        form.update()

        self.assertIn("Please fix indicated errors.",
                      ptah.view.render_messages(form.request))

    def test_model_edit(self):
        from ptah.manage.model import ModelModule, EditRecord

        content = Content1()
        content.title = 'Content test'

        Session = ptah.get_session()
        Session.add(content)
        Session.flush()

        rowid = content.__id__
        transaction.commit()

        mod = ModelModule(None, DummyRequest())
        model = mod['content1'][rowid]

        form = EditRecord(
            model, DummyRequest(
                POST={'title': 'Content', 'form.buttons.modify': 'Modify'}))
        form.csrf = False
        form.update()

        self.assertEqual(form.label, 'Record id: %s'%rowid)

        self.assertIn("Model record has been modified.",
                      ptah.view.render_messages(form.request))
        transaction.commit()

        Session = ptah.get_session()
        content = Session.query(Content1) \
            .filter(Content1.__id__ == rowid).first()
        self.assertEqual(content.title, 'Content')

    def test_model_edit_node(self):
        from ptah.manage.model import ModelModule, EditRecord

        content = Content2()
        content.title = 'Content test'

        Session = ptah.get_session()
        Session.add(content)
        Session.flush()

        rowid = content.__id__
        transaction.commit()

        mod = ModelModule(None, DummyRequest())
        model = mod['content2'][rowid]

        form = EditRecord(
            model, DummyRequest(
                POST={'title': 'Content', 'form.buttons.modify': 'Modify'}))
        form.csrf = False
        form.update()

        self.assertIn("Model record has been modified.",
                      ptah.view.render_messages(form.request))
        transaction.commit()

        Session = ptah.get_session()
        content = Session.query(Content2) \
            .filter(Content2.__id__ == rowid).first()
        self.assertEqual(content.title, 'Content')
