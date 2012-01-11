import transaction
from ptah import cms, config
from ptah.testing import PtahTestCase
from pyramid.exceptions import ConfigurationConflictError


class TestApplicationFactoryRegistration(PtahTestCase):

    _init_ptah = False

    def _make_app(self):
        global TestApplicationRoot
        class TestApplicationRoot(cms.ApplicationRoot):
            __type__ = cms.Type('app')

        return TestApplicationRoot

    def test_app_factory(self):
        import ptah.cms
        ApplicationRoot = self._make_app()

        self.init_ptah()

        factory = ptah.cms.ApplicationFactory(
            ApplicationRoot, '/test', 'root', 'Root App')

        self.assertTrue(factory.id == 'test')
        self.assertTrue(factory.path == '/test/')
        self.assertTrue(factory.name == 'root')
        self.assertTrue(factory.title == 'Root App')
        self.assertTrue(factory.policy is ptah.cms.ApplicationPolicy)

        root = factory(self.request)
        r_uri = root.__uri__

        self.assertTrue(isinstance(root, ApplicationRoot))
        self.assertTrue(root.title == 'Root App')
        self.assertTrue(root.__name__ == 'root')
        self.assertTrue(root.__root_path__ == '/test/')
        self.assertTrue(root.__resource_url__(None, {}) == '/test/')
        self.assertTrue(self.request.root is root)
        transaction.commit()

        root = factory(self.request)
        self.assertEqual(root.__uri__, r_uri)
        transaction.commit()

        root = ptah.resolve(r_uri)
        self.assertEqual(root.__uri__, r_uri)

        factory = ptah.cms.ApplicationFactory(
            ApplicationRoot, '', 'root', 'Root App')
        self.assertTrue(factory.default_root)

    def test_app_factory_mutiple(self):
        import ptah.cms

        factory1 = ptah.cms.ApplicationFactory(
            TestApplicationRoot, '/app1', 'app1', 'Root App1')
        factory2 = ptah.cms.ApplicationFactory(
            TestApplicationRoot, '/app2', 'app2', 'Root App2')

        root1 = factory1()
        root2 = factory2()

        self.assertTrue(root1.__root_path__ == '/app1/')
        self.assertTrue(root2.__root_path__ == '/app2/')
        self.assertTrue(root1.__uri__ != root2.__uri__)

    def test_app_factory_with_parent(self):
        import ptah.cms

        factory1 = ptah.cms.ApplicationFactory(
            TestApplicationRoot, '/app1', 'app1', 'Root App1')
        factory2 = ptah.cms.ApplicationFactory(
            TestApplicationRoot, '/app2', 'app2', 'Root App2',
            parent_factory = factory1)

        root1 = factory1()
        root2 = factory2()
        self.assertTrue(root2.__parent__.__parent__.__uri__ == root1.__uri__)

    def test_app_factory_mutiple_same_name(self):
        import ptah.cms

        factory1 = ptah.cms.ApplicationFactory(
            TestApplicationRoot, '/', 'root1', 'Root App1')
        factory2 = ptah.cms.ApplicationFactory(
            TestApplicationRoot, '/', 'root2', 'Root App2')

        self.assertRaises(ConfigurationConflictError, self.init_ptah)

    def test_app_factory_mutiple_same_applications(self):
        import ptah.cms
        self.init_ptah()

        factory1 = ptah.cms.ApplicationFactory(
            TestApplicationRoot, '/app1', 'root', 'Root App')
        factory2 = ptah.cms.ApplicationFactory(
            TestApplicationRoot, '/app2', 'root', 'Root App')

        root1 = factory1()
        uri1 = root1.__uri__
        self.assertTrue(root1.__root_path__ == '/app1/')
        self.assertTrue(root1.__resource_url__(None, {}) == '/app1/')
        transaction.commit()

        root2 = factory2()

        self.assertTrue(root2.__uri__ == uri1)
        self.assertTrue(root2.__root_path__ == '/app2/')
        self.assertTrue(root2.__resource_url__(None, {}) == '/app2/')

    def test_app_factory_policy(self):
        import ptah.cms

        class CustomPolicy(ptah.cms.ApplicationPolicy):
            pass

        factory = ptah.cms.ApplicationFactory(
            TestApplicationRoot, '/app1', 'root', 'Root App', CustomPolicy)

        root = factory(self.request)
        self.assertTrue(isinstance(root.__parent__, CustomPolicy))


class TestApplicationFactoryCustom(PtahTestCase):

    def test_app_factory_custom_app(self):
        import ptah.cms

        class CustomApplication(ptah.cms.ApplicationRoot):

            __type__ = ptah.cms.Type('customapp', 'Custom app')

        CustomApplication.__type__.cls = CustomApplication

        factory = ptah.cms.ApplicationFactory(
            CustomApplication, '/', 'root', 'Root App')

        root = factory()
        self.assertTrue(isinstance(root, CustomApplication))

        u_root = root.__uri__
        transaction.commit()

        root = factory()
        self.assertEqual(root.__uri__, u_root)

    def test_app_factory_custom_app2(self):
        import ptah.cms

        class CustomApplication2(ptah.cms.ApplicationRoot):

            __type__ = ptah.cms.Type('customapp', 'Custom app')

        CustomApplication2.__type__.cls = CustomApplication2

        factory = ptah.cms.ApplicationFactory(
            CustomApplication2, '/', 'root', 'Root App')

        root = factory()
        self.assertTrue(isinstance(root, CustomApplication2))

        u_root = root.__uri__
        transaction.commit()

        root = factory()
        self.assertEqual(root.__uri__, u_root)
