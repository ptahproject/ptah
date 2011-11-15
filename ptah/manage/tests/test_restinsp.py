import ptah
from pyramid.testing import DummyRequest

from base import Base


class TestRestInspectorModule(Base):

    def test_rest_module(self):
        from ptah.manage.rest import RestModule
        from ptah.manage.manage import CONFIG, PtahManageRoute

        request = DummyRequest()

        ptah.authService.set_userid('test')
        CONFIG['managers'] = ('*',)
        mr = PtahManageRoute(request)
        mod = mr['rest']

        self.assertIsInstance(mod, RestModule)

    def test_view_view(self):
        from ptah.manage.rest import RestModule, RestModuleView

        request = DummyRequest()

        mod = RestModule(None, request)

        res = RestModuleView.__renderer__(mod, request)
        self.assertEqual(res.status, '200 OK')

        view = RestModuleView(mod, request)
        view.update()

        self.assertEqual(
            view.appurl, request.application_url)
        self.assertEqual(
            view.url, '%s/__rest__/cms/' % request.application_url)
