import ptah
from pyramid.testing import DummyRequest

from base import Base


class TestTemplatesModule(Base):

    def test_tmpls_module(self):
        from ptah.manage import PtahManageRoute
        from ptah_modules.templates import TemplatesModule
        
        request = DummyRequest()

        ptah.authService.set_userid('test')
        ptah.PTAH_CONFIG['managers'] = ('*',)
        mr = PtahManageRoute(request)
        mod = mr['templates']

        self.assertIsInstance(mod, TemplatesModule)

    def test_tmpls_view(self):
        from ptah_modules.templates import TemplatesModule, TemplatesView
        
        request = DummyRequest()

        mod = TemplatesModule(None, request)

        res = TemplatesView.__renderer__(mod, request)
        self.assertEqual(res.status, '200 OK')

    # fixme: memphis.view.tmpl
    def test_tmpls_view_pkg(self):
        from ptah_modules.templates import TemplatesModule, TemplatesView
        
        request = DummyRequest(params={'pkg': 'ptah_modules'})

        mod = TemplatesModule(None, request)

        res = TemplatesView.__renderer__(mod, request)
        self.assertEqual(res.status, '200 OK')
