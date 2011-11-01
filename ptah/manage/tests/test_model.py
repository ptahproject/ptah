import transaction
import ptah
from ptah import cms, config
from pyramid.testing import DummyRequest
from pyramid.httpexceptions import HTTPFound

from base import Base


class Content1(cms.Content):
    __type__ = cms.Type('content1')


class Content2(cms.Content):
    __type__ = cms.Type('content2')


class TestModelModule(Base):

    def test_model_module(self):
        from ptah.manage.model import ModelModule
        from ptah.manage.manage import PtahManageRoute

        request = DummyRequest()

        ptah.authService.set_userid('test')
        ptah.PTAH_CONFIG['managers'] = ('*',)
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
