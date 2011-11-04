import ptah
import os.path
import pkg_resources
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

    def test_templs_view_pkg(self):
        from ptah.view import tmpl
        from ptah.manage.templates import TemplatesModule, TemplatesView

        dist = pkg_resources.get_distribution('ptah')
        path = os.path.join(
            dist.location, 'ptah', 'manage', 'templates', 'template.pt')
        tmpl.registry['ptah.manage'] = {
            'template.pt': [path,'title','',None,'ptah.manage']}

        request = DummyRequest(params={'pkg': 'ptah.manage'})

        mod = TemplatesModule(None, request)

        res = TemplatesView.__renderer__(mod, request)
        self.assertEqual(res.status, '200 OK')
        self.assertIn('template.pt', res.body)

    def test_templs_view_template(self):
        from ptah.view import tmpl
        from ptah.manage.templates import TemplatesModule, ViewTemplate

        request = DummyRequest(params={'pkg': 'ptah.manage',
                                       'template': 'template.pt'})

        mod = TemplatesModule(None, request)

        dist = pkg_resources.get_distribution('ptah')
        path = os.path.join(
            dist.location, 'ptah', 'manage', 'templates', 'template.pt')
        tmpl.registry['ptah.manage'] = {'template.pt': [path]}

        res = ViewTemplate.__renderer__(mod, request)

        self.assertEqual(res.status, '200 OK')
        self.assertIn('ptah.manage: template.pt', res.body)
