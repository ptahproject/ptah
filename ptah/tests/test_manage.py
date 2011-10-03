import ptah
import transaction
import simplejson
from memphis import config, view
from pyramid.testing import DummyRequest
from pyramid.httpexceptions import HTTPNotFound, HTTPForbidden

from base import Base


class TestManageModule(Base):

    def tearDown(self):
        config.cleanUp(self.__class__.__module__)
        super(TestManageModule, self).tearDown()

    def test_manage_module(self):
        from ptah.manage import MODULES, PtahManageRoute

        global TestModule
        class TestModule(ptah.PtahModule):
            """ module description """

            title = 'Test module'
            ptah.manageModule('test-module')

        self._init_memphis()
        self.assertIn('test-module', MODULES)

        request = self._makeRequest()

        self.assertRaises(HTTPForbidden, PtahManageRoute, request)

        ptah.authService.setUserId('test-user')

        self.assertRaises(HTTPForbidden, PtahManageRoute, request)

        def accessManager(id):
            return True

        ptah.setAccessManager(accessManager)

        route = PtahManageRoute(request)
        mod = route['test-module']
        self.assertIsInstance(mod, TestModule)
        self.assertTrue(mod.available())
        self.assertEqual(mod.__name__, 'test-module')
        self.assertEqual(mod.url(), 'test-module/')

        self.assertRaises(KeyError, route.__getitem__, 'unknown')

    def test_manage_access_manager(self):
        from ptah.manage import PtahAccessManager
        from ptah.settings import PTAH_CONFIG

        PTAH_CONFIG.managers = ['*']

        self.assertTrue(PtahAccessManager('test:user'))

        PTAH_CONFIG.managers = ['admin@ptahproject.org']

        self.assertFalse(PtahAccessManager('test:user'))

        class Principal(object):
            id = 'test-user'
            login = 'admin@ptahproject.org'

        principal = Principal()

        @ptah.resolver('test')
        def principalResolver(uri):
            return principal

        self.assertTrue(PtahAccessManager('test:user'))

    def test_manage_view(self):
        from ptah.manage import PtahManageRoute, ManageView

        global TestModule
        class TestModule(ptah.PtahModule):
            """ module description """

            title = 'Test module'
            ptah.manageModule('test-module')

        def accessManager(id):
            return True

        ptah.setAccessManager(accessManager)
        ptah.authService.setUserId('test-user')

        self._init_memphis()

        request = self._makeRequest()
        route = PtahManageRoute(request)

        view = ManageView(route, request)
        view.update()

        self.assertIsInstance(view.modules[-1], TestModule)

    def test_manage_layout(self):
        from ptah.manage import PtahManageRoute, LayoutPage

        global TestModule
        class TestModule(ptah.PtahModule):
            """ module description """

            title = 'Test module'
            ptah.manageModule('test-module')

        class Content(object):
            __parent__ = None

        self._init_memphis()

        request = self._makeRequest()

        mod = TestModule(None, request)
        content = Content()
        content.__parent__ = mod

        layout = LayoutPage(mod, request)
        layout.viewcontext = content
        layout.update()

        self.assertIs(layout.module, mod)


class TestInstrospection(Base):

    def tearDown(self):
        config.cleanUp(self.__class__.__module__)
        super(TestInstrospection, self).tearDown()

    def test_manage_module(self):
        from ptah.manage import INTROSPECTIONS, introspection

        global TestModule
        class TestModule(object):
            """ module description """

            title = 'Test module'
            introspection('test-module')

        self._init_memphis()
        self.assertIn('test-module', INTROSPECTIONS)
        self.assertIs(INTROSPECTIONS['test-module'], TestModule)
