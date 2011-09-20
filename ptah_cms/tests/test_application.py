import transaction
from memphis import config

from base import Base


class TestApplication(Base):

    def test_app(self):
        import ptah_cms

        self.assertEqual(
            ptah_cms.Session.query(ptah_cms.ApplicationRoot).all(), [])

        root = ptah_cms.ApplicationRoot.getRoot(
            name='test', title='Test application')
        
        self.assertTrue(isinstance(root, ptah_cms.ApplicationRoot))
        self.assertTrue(root.title == 'Test application')
        self.assertTrue(root.__name__ == 'test')
        self.assertTrue(root.__path__ == '/%s/'%root.__uuid__)

        # __resource_url__ always same as __root_path__
        self.assertTrue(root.__resource_url__(None, {}) == root.__root_path__)

        self.assertEqual(
            len(ptah_cms.Session.query(ptah_cms.ApplicationRoot).all()), 1)

        uuid = root.__uuid__

        transaction.commit()

        root2 = ptah_cms.ApplicationRoot.getRoot(
            name='test', title='Test application')

        self.assertEqual(uuid, root2.__uuid__)
        self.assertEqual(
            len(ptah_cms.Session.query(ptah_cms.ApplicationRoot).all()), 1)


class TestApplicationFactoryRegistration(Base):
    
    def _setup_memphis(self):
        pass

    def test_app_factory(self):
        import ptah_cms
        self._init_memphis()

        factory = ptah_cms.ApplicationFactory('/test', 'root', 'Root App')

        self.assertTrue(factory.id == 'test')
        self.assertTrue(factory.path == '/test/')
        self.assertTrue(factory.name == 'root')
        self.assertTrue(factory.title == 'Root App')
        self.assertTrue(factory.policy is ptah_cms.ApplicationPolicy)

        self._setRequest(self._makeRequest())

        root = factory(self.request)

        self.assertTrue(isinstance(root, ptah_cms.ApplicationRoot))
        self.assertTrue(root.title == 'Root App')
        self.assertTrue(root.__name__ == 'root')
        self.assertTrue(root.__root_path__ == '/test/')
        self.assertTrue(self.request.root is root)

    def test_app_factory_mutiple(self):
        import ptah_cms

        factory1 = ptah_cms.ApplicationFactory('/app1', 'app1', 'Root App1')
        factory2 = ptah_cms.ApplicationFactory('/app2', 'app2', 'Root App2')

        root1 = factory1()
        root2 = factory2()

        self.assertTrue(root1.__root_path__ == '/app1/')
        self.assertTrue(root2.__root_path__ == '/app2/')
        self.assertTrue(root1.__uuid__ != root2.__uuid__)

    def test_app_factory_mutiple_same_name(self):
        import ptah_cms

        factory1 = ptah_cms.ApplicationFactory('/test', 'root', 'Root App1')
        factory2 = ptah_cms.ApplicationFactory('/', 'root', 'Root App2')

        self.assertRaises(config.ConflictError, self._init_memphis)

    def test_app_factory_mutiple_same_applications(self):
        import ptah_cms
        self._init_memphis()

        factory1 = ptah_cms.ApplicationFactory('/app1', 'root', 'Root App')
        factory2 = ptah_cms.ApplicationFactory('/app2', 'root', 'Root App')

        root1 = factory1()
        uuid1 = root1.__uuid__
        self.assertTrue(root1.__root_path__ == '/app1/')
        transaction.commit()
        
        root2 = factory2()

        self.assertTrue(root2.__root_path__ == '/app2/')
        self.assertTrue(root2.__uuid__ == uuid1)

    def test_app_factory_policy(self):
        import ptah_cms

        class CustomPolicy(ptah_cms.ApplicationPolicy):
            pass

        factory = ptah_cms.ApplicationFactory(
            '/app1', 'root', 'Root App', CustomPolicy)

        root = factory(self._makeRequest())
        self.assertTrue(isinstance(root.__parent__, CustomPolicy))
