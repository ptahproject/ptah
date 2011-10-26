import ptah
import transaction
import simplejson
from ptah import config, view
from pyramid.testing import DummyRequest
from pyramid.httpexceptions import HTTPNotFound, HTTPForbidden

from base import Base


class TestManageModule(Base):

    def setUp(self):
        self._setup_pyramid()

    def tearDown(self):
        config.cleanup_system(self.__class__.__module__)
        super(TestManageModule, self).tearDown()

    def test_manage_module(self):
        from ptah.manage.manage import \
           module, MANAGE_ID, PtahModule, PtahManageRoute,\
           set_access_manager

        global TestModule
        class TestModule(PtahModule):
            """ module description """

            title = 'Test module'
            module('test-module')

        self._init_ptah()

        MODULES = config.registry.storage[MANAGE_ID]
        self.assertIn('test-module', MODULES)

        request = self._makeRequest()

        self.assertRaises(HTTPForbidden, PtahManageRoute, request)

        ptah.authService.set_userid('test-user')

        self.assertRaises(HTTPForbidden, PtahManageRoute, request)

        def accessManager(id):
            return True

        set_access_manager(accessManager)

        route = PtahManageRoute(request)
        mod = route['test-module']
        self.assertIsInstance(mod, TestModule)
        self.assertTrue(mod.available())
        self.assertEqual(mod.__name__, 'test-module')
        self.assertEqual(mod.url(), 'test-module/')

        self.assertRaises(KeyError, route.__getitem__, 'unknown')

    def test_manage_access_manager(self):
        from ptah.settings import PTAH_CONFIG
        from ptah.manage.manage import PtahAccessManager

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

        self._init_ptah()
        self.assertTrue(PtahAccessManager('test:user'))

    def test_manage_view(self):
        from ptah.manage.manage import \
            module, PtahModule, PtahManageRoute, ManageView, \
            set_access_manager

        global TestModule
        class TestModule(PtahModule):
            """ module description """

            title = 'Test module'
            module('test-module')

        def accessManager(id):
            return True

        set_access_manager(accessManager)
        ptah.authService.set_userid('test-user')

        self._init_ptah()

        request = self._makeRequest()
        route = PtahManageRoute(request)

        view = ManageView(route, request)
        view.update()

        self.assertIsInstance(view.modules[-1], TestModule)

    def test_manage_layout(self):
        from ptah.manage.manage import \
            module, PtahModule, PtahManageRoute, LayoutManage

        global TestModule
        class TestModule(PtahModule):
            """ module description """

            title = 'Test module'
            module('test-module')

        class Content(object):
            __parent__ = None

        self._init_ptah()

        request = self._makeRequest()

        mod = TestModule(None, request)
        content = Content()
        content.__parent__ = mod
        request.context = content

        layout = LayoutManage(mod, request)
        layout.viewcontext = content
        layout.update()

        self.assertIs(layout.module, mod)


class TestInstrospection(Base):

    def setUp(self):
        self._setup_pyramid()

    def tearDown(self):
        config.cleanup_system(self.__class__.__module__)
        super(TestInstrospection, self).tearDown()

    def test_manage_module(self):
        from ptah.manage.manage import INTROSPECT_ID, introspection

        global TestModule
        class TestModule(object):
            """ module description """

            title = 'Test module'
            introspection('test-module')

        self._init_ptah()

        INTROSPECTIONS = config.registry.storage[INTROSPECT_ID]
        self.assertIn('test-module', INTROSPECTIONS)
        self.assertIs(INTROSPECTIONS['test-module'], TestModule)
