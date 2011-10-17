import ptah
from pyramid.testing import DummyRequest

from base import Base


class TestTemplatesModule(Base):

    def test_tmpls_module(self):
        from ptah.manage.manage import PtahManageRoute
        from ptah.manage.templates import TemplatesModule

        request = DummyRequest()

        ptah.authService.set_userid('test')
        ptah.PTAH_CONFIG['managers'] = ('*',)
        mr = PtahManageRoute(request)
        mod = mr['templates']

        self.assertIsInstance(mod, TemplatesModule)

    def test_tmpls_view(self):
        from ptah.manage.templates import TemplatesModule, TemplatesView

        request = DummyRequest()

        mod = TemplatesModule(None, request)

        res = TemplatesView.__renderer__(mod, request)
        self.assertEqual(res.status, '200 OK')

    # fixme: ptah.view.tmpl
    def test_tmpls_view_pkg(self):
        from ptah.manage.templates import TemplatesModule, TemplatesView

        request = DummyRequest(params={'pkg': 'ptah.manage'})

        mod = TemplatesModule(None, request)

        res = TemplatesView.__renderer__(mod, request)
        self.assertEqual(res.status, '200 OK')
