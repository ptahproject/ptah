import ptah
from pyramid.testing import DummyRequest

from base import Base


class TestPermissionsModule(Base):

    def test_perms_module(self):
        from ptah.manage import PtahManageRoute
        from ptah_modules.permissions import PermissionsModule
        
        request = DummyRequest()

        ptah.authService.set_userid('test')
        ptah.PTAH_CONFIG['managers'] = ('*',)
        mr = PtahManageRoute(request)
        mod = mr['permissions']

        self.assertIsInstance(mod, PermissionsModule)

    def test_perms_view(self):
        from ptah_modules.permissions import PermissionsModule, PermissionsView
        
        request = DummyRequest()

        mod = PermissionsModule(None, request)

        res = PermissionsView.__renderer__(mod, request)
        self.assertEqual(res.status, '200 OK')

    def test_perms_roles(self):
        from ptah_modules.permissions import PermissionsModule, RolesView
        
        request = DummyRequest()

        mod = PermissionsModule(None, request)

        res = RolesView.__renderer__(mod, request)
        self.assertEqual(res.status, '200 OK')
