import ptah
from ptah import config
from pyramid.testing import DummyRequest
from pyramid.httpexceptions import HTTPForbidden

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
           PtahAccessManager, set_access_manager

        global TestModule
        class TestModule(PtahModule):
            """ module description """

            title = 'Test module'
            module('test-module')

        self._init_ptah()

        set_access_manager(PtahAccessManager)

        MODULES = config.get_cfg_storage(MANAGE_ID)
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
        self.assertEqual(mod.url(), '/ptah-manage/test-module')

        self.assertRaises(KeyError, route.__getitem__, 'unknown')

    def test_manage_access_manager(self):
        from ptah.manage.manage import CONFIG
        from ptah.manage.manage import PtahAccessManager

        CONFIG['managers'] = ['*']

        self.assertTrue(PtahAccessManager('test:user'))

        CONFIG['managers'] = ['admin@ptahproject.org']

        self.assertFalse(PtahAccessManager('test:user'))

        class Principal(object):
            id = 'test-user'
            login = 'admin@ptahproject.org'

        principal = Principal()

        @ptah.resolver('test')
        def principalResolver(uri):
            return principal

        self._init_ptah()

        CONFIG['managers'] = ['admin@ptahproject.org']
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

        self._init_ptah()

        set_access_manager(accessManager)
        ptah.authService.set_userid('test-user')

        request = self._makeRequest()
        route = PtahManageRoute(request)

        v = ManageView(route, request)
        v.update()

        self.assertIsInstance(v.modules[-1], TestModule)

    def test_manage_traverse(self):
        from ptah.manage.manage import \
            module, PtahModule, PtahManageRoute, set_access_manager

        global TestModule
        class TestModule(PtahModule):
            """ module description """

            title = 'Test module'
            module('test-module')

        def accessManager(id):
            return True

        self._init_ptah()

        set_access_manager(accessManager)
        ptah.authService.set_userid('test-user')

        request = self._makeRequest()
        route = PtahManageRoute(request)

        mod = route['test-module']
        self.assertIsInstance(mod, TestModule)

    def test_manage_disable_modules(self):
        from ptah.manage.manage import CONFIG, \
            module, PtahModule, PtahManageRoute, ManageView, set_access_manager

        global TestModule
        class TestModule(PtahModule):
            """ module description """

            title = 'Test module'
            module('test-module')

        def accessManager(id):
            return True

        self._init_ptah()

        set_access_manager(accessManager)
        ptah.authService.set_userid('test-user')

        CONFIG['disable_modules'] = ('test-module',)

        request = DummyRequest()
        route = PtahManageRoute(request)

        view = ManageView(route, request)
        view.update()

        for mod in view.modules:
            self.assertFalse(isinstance(mod, TestModule))

    def test_manage_disable_modules_traverse(self):
        from ptah.manage.manage import CONFIG, \
            module, PtahModule, PtahManageRoute, set_access_manager

        global TestModule
        class TestModule(PtahModule):
            """ module description """

            title = 'Test module'
            module('test-module')

        def accessManager(id):
            return True

        self._init_ptah()

        set_access_manager(accessManager)
        ptah.authService.set_userid('test-user')

        CONFIG['disable_modules'] = ('test-module',)

        request = DummyRequest()
        route = PtahManageRoute(request)

        self.assertRaises(KeyError, route.__getitem__, 'test-module')

    def test_manage_layout(self):
        from ptah.manage.manage import \
            module, PtahModule, LayoutManage

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

        INTROSPECTIONS = config.get_cfg_storage(INTROSPECT_ID)
        self.assertIn('test-module', INTROSPECTIONS)
        self.assertIs(INTROSPECTIONS['test-module'], TestModule)
