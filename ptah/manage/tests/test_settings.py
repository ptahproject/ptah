import ptah
from ptah.testing import PtahTestCase
from pyramid.testing import DummyRequest
from pyramid.view import render_view_to_response


class TestSettingsModule(PtahTestCase):

    def test_settings_module(self):
        from ptah.manage.manage import PtahManageRoute
        from ptah.manage.settings import SettingsModule

        request = DummyRequest()

        ptah.auth_service.set_userid('test')
        cfg = ptah.get_settings(ptah.CFG_ID_PTAH, self.registry)
        cfg['managers'] = ('*',)
        mr = PtahManageRoute(request)
        mod = mr['settings']

        self.assertIsInstance(mod, SettingsModule)

    def test_settings_view(self):
        from ptah.manage.settings import SettingsModule, SettingsView

        request = DummyRequest()

        mod = SettingsModule(None, request)

        res = render_view_to_response(mod, request, '', False)
        self.assertEqual(res.status, '200 OK')
