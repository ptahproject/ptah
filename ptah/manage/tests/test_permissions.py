import ptah
from pyramid.testing import DummyRequest

from base import Base


class TestPermissionsModule(Base):

    def test_perms_module(self):
        from ptah.manage.manage import CONFIG, PtahManageRoute
        from ptah.manage.permissions import PermissionsModule

        request = DummyRequest()

        ptah.authService.set_userid('test')
        CONFIG['managers'] = ('*',)
        mr = PtahManageRoute(request)
        mod = mr['permissions']

        self.assertIsInstance(mod, PermissionsModule)

    def test_perms_view(self):
        from ptah.manage.permissions import PermissionsModule, PermissionsView

        request = DummyRequest()

        mod = PermissionsModule(None, request)

        res = PermissionsView.__renderer__(mod, request)
        self.assertEqual(res.status, '200 OK')

    def test_perms_roles(self):
        from ptah.manage.permissions import PermissionsModule, RolesView

        request = DummyRequest()

        mod = PermissionsModule(None, request)

        res = RolesView.__renderer__(mod, request)
        self.assertEqual(res.status, '200 OK')
