import sqlalchemy as sqla
import transaction
import ptah
from ptah import cms
from webob.multidict import MultiDict
from pyramid.testing import DummyRequest
from pyramid.httpexceptions import HTTPFound

from base import Base


class Content1(cms.Content):
    __type__ = cms.Type('content1')


class Content2(cms.Node):
    __type__ = cms.Type('content2')

    title = sqla.Column(sqla.Unicode, default=u'')


class TestModelModule(Base):

    def test_model_module(self):
        from ptah.manage.model import ModelModule
        from ptah.manage.manage import CONFIG, PtahManageRoute

        request = DummyRequest()

        ptah.authService.set_userid('test')
        CONFIG['managers'] = ('*',)
        mr = PtahManageRoute(request)
        mod = mr['models']

        self.assertIsInstance(mod, ModelModule)

    def test_model_view(self):
        from ptah.manage.model import ModelModule, ModelModuleView

        request = DummyRequest()

        mod = ModelModule(None, request)

        res = ModelModuleView.__renderer__(mod, request)
        self.assertEqual(res.status, '200 OK')
        self.assertIn('content1', res.body)
        self.assertIn('content2', res.body)

    def test_model_view_disabled(self):
        from ptah.manage.manage import CONFIG
        from ptah.manage.model import ModelModule, ModelModuleView

        CONFIG['disable_models'] = ['cms-type:content2']

        request = DummyRequest()

        mod = ModelModule(None, request)

        res = ModelModuleView.__renderer__(mod, request)
        self.assertEqual(res.status, '200 OK')
        self.assertIn('content1', res.body)
        self.assertNotIn('content2', res.body)

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
        content.title = u'Content test'

        ptah.cms.Session.add(content)
        ptah.cms.Session.flush()

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
                POST=MultiDict({'form.buttons.remove': 'Remove'})))
        form.csrf = False
        form.update()

        self.assertIn("Please select records for removing.",
                      form.request.session['msgservice'][0])

    def test_model_remove(self):
        from ptah.manage.model import ModelModule, ModelView

        content = Content1()
        content.title = u'Content test'

        ptah.cms.Session.add(content)
        ptah.cms.Session.flush()

        rowid = content.__id__
        transaction.commit()

        mod = ModelModule(None, DummyRequest())
        model = mod['content1']

        form = ModelView(
            model, DummyRequest(
                POST=MultiDict({'rowid':rowid,
                                'form.buttons.remove': 'Remove'})))
        form.csrf = False
        try:
            form.update()
        except Exception, res:
            pass

        self.assertIsInstance(res, HTTPFound)

        transaction.commit()

        rec = ptah.cms.Session.query(Content1).filter(
            Content1.__id__ == rowid).first()
        self.assertIsNone(rec)

    def test_model_list(self):
        from ptah.manage.model import ModelModule, ModelView

        content = Content1()
        content.title = u'Content test'

        ptah.cms.Session.add(content)
        ptah.cms.Session.flush()

        rowid = content.__id__
        transaction.commit()

        mod = ModelModule(None, DummyRequest())
        model = mod['content1']

        res = ModelView.__renderer__(model, DummyRequest())
        self.assertIn('value="%s"'%rowid, res.body)

        res = ModelView.__renderer__(model, DummyRequest(
                params={'batch': 0}))
        self.assertIn('value="%s"'%rowid, res.body)

        res = ModelView.__renderer__(model, DummyRequest(
                params={'batch': 'unknown'}))
        self.assertIn('value="%s"'%rowid, res.body)

    def test_model_add(self):
        from ptah.manage.model import ModelModule, ModelView

        mod = ModelModule(None, DummyRequest())
        model = mod['content1']

        form = ModelView(
            model, DummyRequest(
                POST=MultiDict({'form.buttons.add': 'Add'})))
        form.csrf = False
        try:
            form.update()
        except Exception, res:
            pass

        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], 'add.html')


class TestAddRecord(Base):

    def test_model_add_errors(self):
        from ptah.manage.model import ModelModule, AddRecord

        mod = ModelModule(None, DummyRequest())
        model = mod['content1']

        form = AddRecord(
            model, DummyRequest(
                POST=MultiDict({'form.buttons.add': 'Add'})))
        form.csrf = False
        form.update()

        self.assertIn("Please fix indicated errors.",
                      form.request.session['msgservice'][0])

    def test_model_add_back(self):
        from ptah.manage.model import ModelModule, AddRecord

        mod = ModelModule(None, DummyRequest())
        model = mod['content1']

        form = AddRecord(
            model, DummyRequest(
                POST=MultiDict({'form.buttons.back': 'Back'})))
        form.csrf = False
        try:
            form.update()
        except Exception, res:
            pass

        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], '.')

    def test_model_add(self):
        from ptah.manage.model import ModelModule, AddRecord

        mod = ModelModule(None, DummyRequest())
        model = mod['content1']

        form = AddRecord(
            model, DummyRequest(
                POST=MultiDict({'title': u'Test content',
                                'form.buttons.add': 'Add'})))
        form.csrf = False
        try:
            form.update()
        except Exception, res:
            pass

        id = form.record.__id__
        transaction.commit()

        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], './%s/'%id)
        self.assertEqual(len(ptah.cms.Session.query(Content1).all()), 1)

        content = ptah.cms.Session.query(Content1) \
            .filter(Content1.__id__ == id).first()
        self.assertEqual(content.title, u'Test content')

    def test_model_add_node(self):
        from ptah.manage.model import ModelModule, AddRecord

        mod = ModelModule(None, DummyRequest())
        model = mod['content2']

        form = AddRecord(
            model, DummyRequest(
                POST=MultiDict({'title': u'Test content',
                                'form.buttons.add': 'Add'})))
        form.csrf = False
        try:
            form.update()
        except Exception, res:
            pass

        id = form.record.__id__
        transaction.commit()

        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], './%s/'%id)
        self.assertEqual(len(ptah.cms.Session.query(Content2).all()), 1)

        content = ptah.cms.Session.query(Content2) \
            .filter(Content2.__id__ == id).first()
        self.assertEqual(content.title, u'Test content')


class TestEditRecord(Base):

    def test_model_edit_back(self):
        from ptah.manage.model import ModelModule, EditRecord

        content = Content1()
        content.title = u'Content test'

        ptah.cms.Session.add(content)
        ptah.cms.Session.flush()

        rowid = content.__id__
        transaction.commit()

        mod = ModelModule(None, DummyRequest())
        model = mod['content1'][rowid]

        form = EditRecord(
            model, DummyRequest(
                POST=MultiDict({'form.buttons.back': 'Back'})))
        form.csrf = False
        try:
            form.update()
        except Exception, res:
            pass

        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], '../')

    def test_model_edit_errors(self):
        from ptah.manage.model import ModelModule, EditRecord

        content = Content1()
        content.title = u'Content test'

        ptah.cms.Session.add(content)
        ptah.cms.Session.flush()

        rowid = content.__id__
        transaction.commit()

        mod = ModelModule(None, DummyRequest())
        model = mod['content1'][rowid]

        form = EditRecord(
            model, DummyRequest(
                POST=MultiDict({'form.buttons.modify': 'Modify'})))
        form.csrf = False
        form.update()

        self.assertIn("Please fix indicated errors.",
                      form.request.session['msgservice'][0])

    def test_model_edit(self):
        from ptah.manage.model import ModelModule, EditRecord

        content = Content1()
        content.title = u'Content test'

        ptah.cms.Session.add(content)
        ptah.cms.Session.flush()

        rowid = content.__id__
        transaction.commit()

        mod = ModelModule(None, DummyRequest())
        model = mod['content1'][rowid]

        form = EditRecord(
            model, DummyRequest(
                POST=MultiDict({'title': 'Content',
                                'form.buttons.modify': 'Modify'})))
        form.csrf = False
        form.update()

        self.assertEqual(form.label, 'Record id: %s'%rowid)

        self.assertIn("Model record has been modified.",
                      form.request.session['msgservice'][0])
        transaction.commit()

        content = ptah.cms.Session.query(Content1) \
            .filter(Content1.__id__ == rowid).first()
        self.assertEqual(content.title, u'Content')

    def test_model_edit_node(self):
        from ptah.manage.model import ModelModule, EditRecord

        content = Content2()
        content.title = u'Content test'

        ptah.cms.Session.add(content)
        ptah.cms.Session.flush()

        rowid = content.__id__
        transaction.commit()

        mod = ModelModule(None, DummyRequest())
        model = mod['content2'][rowid]

        form = EditRecord(
            model, DummyRequest(
                POST=MultiDict({'title': 'Content',
                                'form.buttons.modify': 'Modify'})))
        form.csrf = False
        form.update()

        self.assertIn("Model record has been modified.",
                      form.request.session['msgservice'][0])
        transaction.commit()

        content = ptah.cms.Session.query(Content2) \
            .filter(Content2.__id__ == rowid).first()
        self.assertEqual(content.title, u'Content')


class TestTypeIntrospect(Base):

    def test_type_introspect(self):
        from ptah.config import directives
        from ptah.manage.model import TypeIntrospection

        data = directives.scan(self.__class__.__module__, set())

        actions = []
        for action in data:
            if action.discriminator[0] == 'ptah-cms:type':
                actions.append(action)

        ti = TypeIntrospection(self.request)
        res = ti.renderActions(*actions)

        self.assertIn('<small>cms-type:content1</small>', res)
        self.assertIn('<small>cms-type:content2</small>', res)
