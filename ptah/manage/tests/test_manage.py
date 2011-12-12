import ptah
from ptah import config
from ptah.testing import PtahTestCase
from pyramid.testing import DummyRequest
from pyramid.httpexceptions import HTTPForbidden


class TestManageModule(PtahTestCase):

    _init_ptah = False

    def test_get_manage_url(self):
        from ptah.manage import get_manage_url
        self.init_ptah()

        self.request.application_url = 'http://example.com'
        self.assertEqual(get_manage_url(self.request),
                         'http://example.com/ptah-manage')

        self.request.application_url = 'http://example.com/'
        self.assertEqual(get_manage_url(self.request),
                         'http://example.com/ptah-manage')

        cfg = ptah.get_settings(ptah.CFG_ID_PTAH, self.registry)
        cfg['manage'] = 'manage'

        self.assertEqual(get_manage_url(self.request),
                         'http://example.com/manage')

    def test_manage_module(self):
        from ptah.manage.manage import \
           module, MANAGE_ID, PtahModule, PtahManageRoute,\
           PtahAccessManager, set_access_manager

        @module('test-module')
        class TestModule(PtahModule):
            """ module description """

            title = 'Test module'

        self.init_ptah()

        set_access_manager(PtahAccessManager)

        MODULES = config.get_cfg_storage(MANAGE_ID)
        self.assertIn('test-module', MODULES)

        self.assertRaises(HTTPForbidden, PtahManageRoute, self.request)

        ptah.auth_service.set_userid('test-user')

        self.assertRaises(HTTPForbidden, PtahManageRoute, self.request)

        def accessManager(id):
            return True

        set_access_manager(accessManager)

        route = PtahManageRoute(self.request)
        mod = route['test-module']
        self.assertIsInstance(mod, TestModule)
        self.assertTrue(mod.available())
        self.assertEqual(mod.__name__, 'test-module')
        self.assertEqual(mod.url(), 'http://example.com/ptah-manage/test-module')

        self.assertRaises(KeyError, route.__getitem__, 'unknown')

    def test_manage_access_manager1(self):
        from ptah.manage.manage import PtahAccessManager
        self.init_ptah()

        cfg = ptah.get_settings(ptah.CFG_ID_PTAH, self.registry)
        cfg['managers'] = ['*']

        self.assertTrue(PtahAccessManager('test:user'))

        cfg['managers'] = ['admin@ptahproject.org']

        self.assertFalse(PtahAccessManager('test:user'))

    def test_manage_access_manager2(self):
        from ptah.manage.manage import PtahAccessManager

        class Principal(object):
            id = 'test-user'
            login = 'admin@ptahproject.org'

        principal = Principal()

        @ptah.resolver('test')
        def principalResolver(uri):
            return principal

        self.init_ptah()

        cfg = ptah.get_settings(ptah.CFG_ID_PTAH, self.registry)
        cfg['managers'] = ['admin@ptahproject.org']
        self.assertTrue(PtahAccessManager('test:user'))

    def test_manage_view(self):
        from ptah.manage.manage import \
            module, PtahModule, PtahManageRoute, ManageView, \
            set_access_manager

        @module('test-module')
        class TestModule(PtahModule):
            """ module description """

            title = 'Test module'

        def accessManager(id):
            return True

        self.init_ptah()

        set_access_manager(accessManager)
        ptah.auth_service.set_userid('test-user')

        route = PtahManageRoute(self.request)

        v = ManageView(route, self.request)
        v.update()

        self.assertIsInstance(v.modules[-1], TestModule)

    def test_manage_view_unavailable(self):
        from ptah.manage.manage import \
            module, PtahModule, PtahManageRoute, ManageView, \
            set_access_manager

        @module('test-module')
        class TestModule(PtahModule):
            """ module description """

            title = 'Test module'

            def available(self):
                return False

        def accessManager(id):
            return True

        self.init_ptah()

        set_access_manager(accessManager)
        ptah.auth_service.set_userid('test-user')

        route = PtahManageRoute(self.request)

        v = ManageView(route, self.request)
        v.update()

        found = False
        for mod in v.modules:
            if isinstance(mod, TestModule): # pragma: no cover
                found = True

        self.assertFalse(found)

    def test_manage_traverse(self):
        from ptah.manage.manage import \
            module, PtahModule, PtahManageRoute, set_access_manager

        @module('test-module')
        class TestModule(PtahModule):
            """ module description """

            title = 'Test module'

        def accessManager(id):
            return True

        self.init_ptah()

        set_access_manager(accessManager)
        ptah.auth_service.set_userid('test-user')

        route = PtahManageRoute(self.request)

        mod = route['test-module']
        self.assertIsInstance(mod, TestModule)

    def test_manage_disable_modules(self):
        from ptah.manage.manage import \
            module, PtahModule, PtahManageRoute, ManageView, set_access_manager

        @module('test-module')
        class TestModule(PtahModule):
            """ module description """

            title = 'Test module'

        def accessManager(id):
            return True

        self.init_ptah()

        set_access_manager(accessManager)
        ptah.auth_service.set_userid('test-user')

        cfg = ptah.get_settings(ptah.CFG_ID_PTAH, self.registry)
        cfg['disable_modules'] = ('test-module',)

        request = DummyRequest()
        route = PtahManageRoute(request)

        view = ManageView(route, request)
        view.update()

        for mod in view.modules:
            self.assertFalse(isinstance(mod, TestModule))

    def test_manage_disable_modules_traverse(self):
        from ptah.manage.manage import \
            module, PtahModule, PtahManageRoute, set_access_manager

        @module('test-module')
        class TestModule(PtahModule):
            """ module description """

            title = 'Test module'

        def accessManager(id):
            return True

        self.init_ptah()

        set_access_manager(accessManager)
        ptah.auth_service.set_userid('test-user')

        cfg = ptah.get_settings(ptah.CFG_ID_PTAH, self.registry)
        cfg['disable_modules'] = ('test-module',)

        request = DummyRequest()
        route = PtahManageRoute(request)

        self.assertRaises(KeyError, route.__getitem__, 'test-module')

    def test_manage_layout(self):
        from ptah.manage.manage import \
            module, PtahModule, LayoutManage

        @module('test-module')
        class TestModule(PtahModule):
            """ module description """

            title = 'Test module'

        class Content(object):
            __parent__ = None

        self.init_ptah()

        mod = TestModule(None, self.request)
        content = Content()
        content.__parent__ = mod
        self.request.context = content

        layout = LayoutManage(mod, self.request)
        layout.viewcontext = content
        layout.context.userid = ''
        layout.update()

        self.assertIs(layout.module, mod)
