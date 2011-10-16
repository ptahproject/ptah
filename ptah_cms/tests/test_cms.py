import transaction
from zope import interface
from memphis import config
from pyramid.httpexceptions import HTTPForbidden

from base import Base


class TestAction(Base):

    def tearDown(self):
        config.cleanup_system(self.__class__.__module__)
        super(TestAction, self).tearDown()

    def test_cms_action_reg(self):
        import ptah_cms

        class Test(object):
            @ptah_cms.action
            def update(self, **data): # pragma: no cover
                pass

        self.assertTrue(hasattr(Test, '__ptahcms_actions__'))

        actions = Test.__ptahcms_actions__
        self.assertIn('update', actions)
        self.assertEqual(actions['update'], ('update', ptah_cms.View))

    def test_cms_action_reg_name(self):
        import ptah_cms

        class Test(object):
            @ptah_cms.action(name='test')
            def update(self, **data): # pragma: no cover
                pass

        actions = Test.__ptahcms_actions__
        self.assertIn('test', actions)
        self.assertEqual(actions['test'], ('update', ptah_cms.View))

    def test_cms_action_reg_permission(self):
        import ptah_cms

        class Test(object):
            @ptah_cms.action(permission='perm')
            def update(self, **data): # pragma: no cover
                pass

        actions = Test.__ptahcms_actions__
        self.assertEqual(actions['update'], ('update', 'perm'))

    def test_cms_action_inherit(self):
        import ptah_cms
        from ptah_cms.cms import buildClassActions

        class Test(object):
            @ptah_cms.action(permission='perm')
            def update(self, **data): # pragma: no cover
                pass

        class Test2(Test):
            pass

        buildClassActions(Test2)

        actions = Test2.__ptahcms_actions__

        self.assertEqual(actions['update'], ('update', 'perm'))
        self.assertIsNot(actions, Test.__ptahcms_actions__)

    def test_cms_action_inherit2(self):
        import ptah_cms
        from ptah_cms.cms import buildClassActions

        class Test(object):
            @ptah_cms.action
            def update(self, **data): # pragma: no cover
                pass

        class Test2(Test):
            @ptah_cms.action
            def create(self, **data): # pragma: no cover
                pass

        buildClassActions(Test2)

        actions = Test2.__ptahcms_actions__

        self.assertEqual(len(actions), 2)
        self.assertIn('update', actions)
        self.assertIn('create', actions)


class TestWrapper(Base):

    def tearDown(self):
        config.cleanup_system(self.__class__.__module__)
        super(TestWrapper, self).tearDown()

    def test_cms_wrapper_not_found(self):
        import ptah_cms
        from ptah_cms.cms import NodeWrapper

        class Test(object):
            @ptah_cms.action
            def update(self, **data): # pragma: no cover
                pass

        wrapper = NodeWrapper(Test())
        self.assertRaises(
            ptah_cms.NotFound, wrapper.__getattr__, 'unknown')

    def test_cms_wrapper_forbidden(self):
        import ptah, ptah_cms
        from ptah_cms.cms import NodeWrapper

        class Test(object):
            @ptah_cms.action(permission=ptah.NOT_ALLOWED)
            def update(self, *args, **data): # pragma: no cover
                return 'test'

        wrapper = NodeWrapper(Test())

        self.assertRaises(
            ptah_cms.Forbidden, wrapper.__getattr__, 'update')

    def test_cms_wrapper(self):
        import ptah, ptah_cms
        from ptah_cms.cms import NodeWrapper

        class Test(object):
            @ptah_cms.action(permission=ptah.NO_PERMISSION_REQUIRED)
            def update(self, *args, **data):
                return 'test'

        wrapper = NodeWrapper(Test())
        self.assertEqual(wrapper.update(), 'test')


class TestCms(Base):

    def _setup_memphis(self):
        pass

    def tearDown(self):
        config.cleanup_system(self.__class__.__module__)
        super(TestCms, self).tearDown()

    def test_cms_not_found(self):
        import ptah_cms

        self.assertRaises(ptah_cms.NotFound, ptah_cms.cms, 'unknown')
        self.assertRaises(ptah_cms.NotFound, ptah_cms.cms, None)

    def test_cms(self):
        import ptah, ptah_cms
        from ptah_cms.cms import NodeWrapper

        class Test(ptah_cms.Content):
            __uri_generator__ = ptah.UriGenerator('test')

            @ptah_cms.action(permission=ptah.NO_PERMISSION_REQUIRED)
            def update(self, *args, **data): # pragma: no cover
                pass

        t = Test()
        wrapper = ptah_cms.cms(t)
        self.assertIsInstance(wrapper, NodeWrapper)
        self.assertIs(wrapper._content, t)

    def test_cms_2(self):
        import ptah, ptah_cms
        from ptah_cms.cms import NodeWrapper

        class Test(ptah_cms.Content):
            __uri_generator__ = ptah.UriGenerator('test')

            @ptah_cms.action(permission=ptah.NO_PERMISSION_REQUIRED)
            def update(self, *args, **data): # pragma: no cover
                pass

        t = Test()

        @ptah.resolver('test')
        def res(uri):
            return t

        self._init_memphis()

        wrapper = ptah_cms.cms('test:1')
        self.assertIsInstance(wrapper, NodeWrapper)
        self.assertIs(wrapper._content, t)
