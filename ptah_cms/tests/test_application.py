import ptah
import transaction
from ptah import config

from base import Base


class TestApplicationFactoryRegistration(Base):

    def _setup_ptah(self):
        pass

    def test_app_factory(self):
        import ptah_cms
        self._init_ptah()

        factory = ptah_cms.ApplicationFactory('/test', 'root', 'Root App')

        self.assertTrue(factory.id == 'test')
        self.assertTrue(factory.path == '/test/')
        self.assertTrue(factory.name == 'root')
        self.assertTrue(factory.title == 'Root App')
        self.assertTrue(factory.policy is ptah_cms.ApplicationPolicy)

        self._setRequest(self._makeRequest())

        root = factory(self.request)
        r_uri = root.__uri__

        self.assertTrue(isinstance(root, ptah_cms.ApplicationRoot))
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

        factory = ptah_cms.ApplicationFactory('', 'root', 'Root App')
        self.assertTrue(factory.default_root)

    def test_app_factory_mutiple(self):
        import ptah_cms

        factory1 = ptah_cms.ApplicationFactory('/app1', 'app1', 'Root App1')
        factory2 = ptah_cms.ApplicationFactory('/app2', 'app2', 'Root App2')

        root1 = factory1()
        root2 = factory2()

        self.assertTrue(root1.__root_path__ == '/app1/')
        self.assertTrue(root2.__root_path__ == '/app2/')
        self.assertTrue(root1.__uri__ != root2.__uri__)

    def test_app_factory_mutiple_same_name(self):
        import ptah_cms

        factory1 = ptah_cms.ApplicationFactory('/test', 'root', 'Root App1')
        factory2 = ptah_cms.ApplicationFactory('/', 'root', 'Root App2')

        self.assertRaises(config.ConflictError, self._init_ptah)

    def test_app_factory_mutiple_same_applications(self):
        import ptah_cms
        self._init_ptah()

        factory1 = ptah_cms.ApplicationFactory('/app1', 'root', 'Root App')
        factory2 = ptah_cms.ApplicationFactory('/app2', 'root', 'Root App')

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
        import ptah_cms

        class CustomPolicy(ptah_cms.ApplicationPolicy):
            pass

        factory = ptah_cms.ApplicationFactory(
            '/app1', 'root', 'Root App', policy=CustomPolicy)

        root = factory(self._makeRequest())
        self.assertTrue(isinstance(root.__parent__, CustomPolicy))


class TestApplicationFactoryCustom(Base):

    def setUp(self):
        super(TestApplicationFactoryCustom, self).setUp()

        import ptah_cms
        ptah_cms.ApplicationFactory._sql_get_root.reset()

    def tearDown(self):
        config.cleanup_system(self.__class__.__module__)
        super(TestApplicationFactoryCustom, self).tearDown()

    def test_app_factory_custom_app(self):
        import ptah_cms

        class CustomApplication(ptah_cms.ApplicationRoot):

            __type__ = ptah_cms.Type('customapp', 'Custom app')

        CustomApplication.__type__.cls = CustomApplication

        factory = ptah_cms.ApplicationFactory(
            '/', 'root', 'Root App', CustomApplication.__type__)

        root = factory()
        self.assertTrue(isinstance(root, CustomApplication))

        u_root = root.__uri__
        transaction.commit()

        root = factory()
        self.assertEqual(root.__uri__, u_root)

    def test_app_factory_custom_app2(self):
        import ptah_cms

        class CustomApplication(ptah_cms.ApplicationRoot):

            __type__ = ptah_cms.Type('customapp', 'Custom app')

        CustomApplication.__type__.cls = CustomApplication

        factory = ptah_cms.ApplicationFactory(
            '/', 'root', 'Root App', CustomApplication)

        root = factory()
        self.assertTrue(isinstance(root, CustomApplication))

        u_root = root.__uri__
        transaction.commit()

        root = factory()
        self.assertEqual(root.__uri__, u_root)
