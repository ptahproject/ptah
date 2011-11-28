from ptah import config
from ptah.testing import PtahTestCase


class TestAction(PtahTestCase):

    def test_cms_action_reg(self):
        import ptah.cms

        class Test(object):
            @ptah.cms.action
            def update(self, **data): # pragma: no cover
                pass

        self.assertTrue(hasattr(Test, '__ptahcms_actions__'))

        actions = Test.__ptahcms_actions__
        self.assertIn('update', actions)
        self.assertEqual(actions['update'], ('update', ptah.cms.View))

    def test_cms_action_reg_name(self):
        import ptah.cms

        class Test(object):
            @ptah.cms.action(name='test')
            def update(self, **data): # pragma: no cover
                pass

        actions = Test.__ptahcms_actions__
        self.assertIn('test', actions)
        self.assertEqual(actions['test'], ('update', ptah.cms.View))

    def test_cms_action_reg_permission(self):
        import ptah.cms

        class Test(object):
            @ptah.cms.action(permission='perm')
            def update(self, **data): # pragma: no cover
                pass

        actions = Test.__ptahcms_actions__
        self.assertEqual(actions['update'], ('update', 'perm'))

    def test_cms_action_inherit(self):
        import ptah.cms
        from ptah.cms.security import build_class_actions

        class Test(object):
            @ptah.cms.action(permission='perm')
            def update(self, **data): # pragma: no cover
                pass

        class Test2(Test):
            pass

        build_class_actions(Test2)

        actions = Test2.__ptahcms_actions__

        self.assertEqual(actions['update'], ('update', 'perm'))
        self.assertIsNot(actions, Test.__ptahcms_actions__)

    def test_cms_action_inherit2(self):
        import ptah.cms
        from ptah.cms.security import build_class_actions

        class Test(object):
            @ptah.cms.action
            def update(self, **data): # pragma: no cover
                pass

        class Test2(Test):
            @ptah.cms.action
            def create(self, **data): # pragma: no cover
                pass

        build_class_actions(Test2)

        actions = Test2.__ptahcms_actions__

        self.assertEqual(len(actions), 2)
        self.assertIn('update', actions)
        self.assertIn('create', actions)


class TestWrapper(PtahTestCase):

    def test_cms_wrapper_not_found(self):
        import ptah.cms
        from ptah.cms.security import NodeWrapper

        class Test(object):
            @ptah.cms.action
            def update(self, **data): # pragma: no cover
                pass

        wrapper = NodeWrapper(Test())
        self.assertRaises(
            ptah.cms.NotFound, wrapper.__getattr__, 'unknown')

    def test_cms_wrapper_forbidden(self):
        import ptah, ptah.cms
        from ptah.cms.security import NodeWrapper

        class Test(object):
            @ptah.cms.action(permission=ptah.NOT_ALLOWED)
            def update(self, *args, **data): # pragma: no cover
                return 'test'

        wrapper = NodeWrapper(Test())

        self.assertRaises(
            ptah.cms.Forbidden, wrapper.__getattr__, 'update')

    def test_cms_wrapper(self):
        import ptah, ptah.cms
        from ptah.cms.security import NodeWrapper

        class Test(object):
            @ptah.cms.action(permission=ptah.NO_PERMISSION_REQUIRED)
            def update(self, *args, **data):
                return 'test'

        wrapper = NodeWrapper(Test())
        self.assertEqual(wrapper.update(), 'test')


class TestCms(PtahTestCase):

    _init_ptah = False

    def test_cms_not_found(self):
        import ptah.cms

        self.assertRaises(ptah.cms.NotFound, ptah.cms.wrap, 'unknown')
        self.assertRaises(ptah.cms.NotFound, ptah.cms.wrap, None)

    def test_cms(self):
        import ptah
        from ptah.cms.security import wrap, NodeWrapper

        class Test(ptah.cms.Content):
            __uri_factory__ = ptah.UriFactory('test')

            @ptah.cms.action(permission=ptah.NO_PERMISSION_REQUIRED)
            def update(self, *args, **data): # pragma: no cover
                pass

        t = Test()
        wrapper = wrap(t)
        self.assertIsInstance(wrapper, NodeWrapper)
        self.assertIs(wrapper._content, t)

    def test_cms_2(self):
        import ptah
        from ptah.cms.security import wrap, NodeWrapper

        class Test(ptah.cms.Content):
            __uri_factory__ = ptah.UriFactory('test')

            @ptah.cms.action(permission=ptah.NO_PERMISSION_REQUIRED)
            def update(self, *args, **data): # pragma: no cover
                pass

        t = Test()

        @ptah.resolver('test')
        def res(uri):
            return t

        self.init_ptah()

        wrapper = wrap('test:1')
        self.assertIsInstance(wrapper, NodeWrapper)
        self.assertIs(wrapper._content, t)
