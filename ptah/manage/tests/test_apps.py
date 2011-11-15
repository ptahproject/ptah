import ptah
from ptah import cms, config
from pyramid.testing import DummyRequest
from pyramid.httpexceptions import HTTPFound

from base import Base

class TestApp1(cms.ApplicationRoot):
    __type__ = cms.Type('app1')


class TestApp2(cms.ApplicationRoot):
    __type__ = cms.Type('app2')


class TestAppsModule(Base):

    def tearDown(self):
        config.cleanup_system(self.__class__.__module__)
        super(TestAppsModule, self).tearDown()

    def test_apps_module(self):
        from ptah.manage.manage import CONFIG, PtahManageRoute
        from ptah.manage.apps import ApplicationsModule

        request = DummyRequest()

        ptah.authService.set_userid('test')
        CONFIG['managers'] = ('*',)
        mr = PtahManageRoute(request)
        mod = mr['apps']

        self.assertIsInstance(mod, ApplicationsModule)

    def test_apps_view(self):
        from ptah.manage.apps import ApplicationsModule
        from ptah.manage.apps import ApplicationsModuleView

        cms.ApplicationFactory(
            TestApp1, '/test1', 'app1', 'Root App 1')

        cms.ApplicationFactory(
            TestApp2, '/test2', 'app2', 'Root App 2')

        self._init_ptah()

        request = DummyRequest()

        mod = ApplicationsModule(None, request)

        res = ApplicationsModuleView.__renderer__(mod, request)
        self.assertEqual(res.status, '200 OK')
        self.assertIn('/test1/', res.body)
        self.assertIn('/test2/', res.body)
        self.assertIn('App1', res.body)
        self.assertIn('App2', res.body)

    def test_apps_traverse(self):
        from ptah.manage.apps import ApplicationsModule
        from ptah.manage.apps import AppFactory

        factory1 = cms.ApplicationFactory(
            TestApp1, '/test1', 'app1', 'Root App 1')

        factory2 = cms.ApplicationFactory(
            TestApp2, '/test2', 'app2', 'Root App 2')

        self._init_ptah()

        request = DummyRequest()

        mod = ApplicationsModule(None, request)

        item = mod['app1']
        self.assertIsInstance(item, AppFactory)
        self.assertIs(item.factory, factory1)
        self.assertIsInstance(item.app, TestApp1)

        item = mod['app2']
        self.assertIsInstance(item, AppFactory)
        self.assertIs(item.factory, factory2)
        self.assertIsInstance(item.app, TestApp2)
        self.assertRaises(KeyError, mod.__getitem__, 'app3')


class TestAppSharingForm(Base):

    def tearDown(self):
        config.cleanup_system(self.__class__.__module__)
        super(TestAppSharingForm, self).tearDown()

    def _make_app(self, request=None):
        from ptah.manage.manage import CONFIG, PtahManageRoute

        class Principal(object):
            id = 'test-user'
            uri = 'test:user'
            login = 'admin@ptahproject.org'

        principal = Principal()

        @ptah.resolver('test')
        def principalResolver(uri):
            return principal

        @ptah.principal_searcher('test')
        def principalSearcher(term):
            return (principal,)

        cms.ApplicationFactory(
            TestApp1, '/test1', 'app1', 'Root App 1')

        cms.ApplicationFactory(
            TestApp2, '/test2', 'app2', 'Root App 2')

        self.TestRole = ptah.Role('test', 'Test role')

        self._init_ptah()

        if request is None:
            request = DummyRequest()

        ptah.authService.set_userid(ptah.SUPERUSER_URI)
        CONFIG['managers'] = ('*',)
        mr = PtahManageRoute(request)
        mod = mr['apps']
        return mod['app1']

    def test_sharingform_search(self):
        from ptah.manage.apps import SharingForm

        app = self._make_app()

        form = SharingForm(app, DummyRequest(
                POST={'form.buttons.search': 'Search',
                      'term': 'search term'}))
        form.csrf = False
        try:
            form.update()
        except Exception, res:
            pass

        self.assertIsInstance(res, HTTPFound)
        self.assertIn('apps-sharing-term', form.request.session)
        self.assertEqual(
            form.request.session['apps-sharing-term'], 'search term')

    def test_sharingform_search_error(self):
        from ptah.manage.apps import SharingForm

        app = self._make_app()

        form = SharingForm(app, DummyRequest(
                POST={'form.buttons.search': 'Search'}))
        form.csrf = False
        form.update()

        self.assertIn('Please specify search term',
                      form.request.session['msgservice'][0])

    def test_sharingform_update(self):
        from ptah.manage.apps import SharingForm

        app = self._make_app()

        form = SharingForm(app, DummyRequest(
                session={'apps-sharing-term': 'email'}))
        form.csrf = False
        form.update()

        self.assertEqual(len(form.users), 1)
        self.assertEqual(form.users[0].uri, 'test:user')
        self.assertIs(form.local_roles, app.app.__local_roles__)
        self.assertEqual(len(form.roles), 1)
        self.assertIs(form.roles[0], self.TestRole)
        self.assertEqual(form.get_principal('test:user').uri, 'test:user')

    def test_sharingform_save(self):
        from ptah.manage.apps import SharingForm

        app = self._make_app()

        form = SharingForm(app, DummyRequest(
                session={'apps-sharing-term': 'email'},
                POST={'form.buttons.save': 'Save',
                      'userid-test:user': 'on',
                      'user-test:user-role:test': 'on'}))
        form.csrf = False
        form.update()

        self.assertIn('test:user', app.app.__local_roles__)
        self.assertIn(self.TestRole.id, app.app.__local_roles__['test:user'])

    def test_sharingform_unset(self):
        from ptah.manage.apps import SharingForm

        app = self._make_app()
        app.app.__local_roles__ = {'test:user': [self.TestRole.id]}

        form = SharingForm(app, DummyRequest(
                session={'apps-sharing-term': 'email'},
                POST={'form.buttons.save': 'Save',
                      'userid-test:user': 'on'}))
        form.csrf = False
        form.update()

        self.assertNotIn('test:user', app.app.__local_roles__)
