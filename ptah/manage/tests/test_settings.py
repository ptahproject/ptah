import ptah
from pyramid.testing import DummyRequest

from base import Base


class TestSettingsModule(Base):

    def test_settings_module(self):
        self._init_ptah()

        from ptah.manage.manage import CONFIG, PtahManageRoute
        from ptah.manage.settings import SettingsModule

        request = DummyRequest()

        ptah.authService.set_userid('test')
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
