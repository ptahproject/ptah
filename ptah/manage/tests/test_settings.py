import ptah
from ptah.testing import PtahTestCase
from pyramid.testing import DummyRequest


class TestSettingsModule(PtahTestCase):

    def test_settings_module(self):
        from ptah.manage.manage import CONFIG, PtahManageRoute
        from ptah.manage.settings import SettingsModule

        request = DummyRequest()

        ptah.auth_service.set_userid('test')
        CONFIG['managers'] = ('*',)
        mr = PtahManageRoute(request)
        mod = mr['settings']

        self.assertIsInstance(mod, SettingsModule)

    def test_settings_view(self):
        from ptah.manage.settings import SettingsModule, SettingsView

        request = DummyRequest()

        mod = SettingsModule(None, request)

        res = SettingsView.__renderer__(mod, request)
        self.assertEqual(res.status, '200 OK')
