import ptah
from ptah import config
from ptah.testing import PtahTestCase
from pyramid.exceptions import ConfigurationConflictError


class TestUIAction(PtahTestCase):

    _init_ptah = False

    def test_uiaction(self):
        class Content(object):
            __name__ = ''

        ptah.uiaction(Content, 'action1', 'Action 1')
        self.init_ptah()

        actions = ptah.list_uiactions(Content(), self.request)

        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0]['id'], 'action1')

    def test_uiaction_conflicts(self):
        class Content(object):
            __name__ = ''

        ptah.uiaction(Content, 'action1', 'Action 1')
        ptah.uiaction(Content, 'action1', 'Action 1')
        self.assertRaises(ConfigurationConflictError, self.init_ptah)

    def test_uiaction_url(self):

        class Content(object):
            __name__ = ''

        ptah.uiaction(Content, 'action1', 'Action 1', action='test.html')
        self.init_ptah()

        actions = ptah.list_uiactions(Content(), self.request)
        self.assertEqual(actions[0]['url'], 'http://example.com/test.html')

    def test_uiaction_absolute_url(self):

        class Content(object):
            __name__ = ''

        ptah.uiaction(
            Content, 'action1', 'Action 1', action='/content/about.html')
        self.init_ptah()

        actions = ptah.list_uiactions(Content(), self.request)
        self.assertEqual(actions[0]['url'],
                         'http://example.com/content/about.html')

    def test_uiaction_custom_url(self):

        class Content(object):
            __name__ = ''

        def customAction(content, request):
            return 'http://github.com/ptahproject'

        ptah.uiaction(Content, 'action1', 'Action 1', action=customAction)

        self.init_ptah()

        actions = ptah.list_uiactions(Content(), self.request)
        self.assertEqual(actions[0]['url'], 'http://github.com/ptahproject')

    def test_uiaction_condition(self):

        class Content(object):
            __name__ = ''

        allow = False
        def condition(content, request):
            return allow

        ptah.uiaction(
            Content, 'action1', 'Action 1',
            action='test.html', condition=condition)

        self.init_ptah()

        actions = ptah.list_uiactions(Content(), self.request)
        self.assertEqual(len(actions), 0)

        allow = True
        actions = ptah.list_uiactions(Content(), self.request)
        self.assertEqual(len(actions), 1)

    def test_uiaction_permission(self):

        class Content(object):
            __name__ = ''

        allow = False
        def check_permission(permission, content, request=None, throw=False):
            return allow

        ptah.uiaction(Content, 'action1', 'Action 1', permission='View')

        self.init_ptah()

        orig_cp = ptah.check_permission
        ptah.check_permission = check_permission

        actions = ptah.list_uiactions(Content(), self.request)
        self.assertEqual(len(actions), 0)

        allow = True
        actions = ptah.list_uiactions(Content(), self.request)
        self.assertEqual(len(actions), 1)

        ptah.check_permission = orig_cp

    def test_uiaction_sort_weight(self):

        class Content(object):
            __name__ = ''

        ptah.uiaction(Content, 'view', 'View', sort_weight=1.0)
        ptah.uiaction(Content, 'action', 'Action', sort_weight=2.0)

        self.init_ptah()

        actions = ptah.list_uiactions(Content(), self.request)

        self.assertEqual(actions[0]['id'], 'view')
        self.assertEqual(actions[1]['id'], 'action')

    def test_uiaction_userdata(self):

        class Content(object):
            __name__ = ''

        ptah.uiaction(Content, 'view', 'View', testinfo='test')

        self.init_ptah()

        actions = ptah.list_uiactions(Content(), self.request)

        self.assertEqual(actions[0]['data'], {'testinfo': 'test'})

    def test_uiaction_category(self):
        class Content(object):
            __name__ = ''

        ptah.uiaction(Content, 'action1', 'Action 1',
                      category='test')

        self.init_ptah()

        request = self.request

        actions = ptah.list_uiactions(Content(), self.request)
        self.assertEqual(len(actions), 0)

        actions = ptah.list_uiactions(Content(), self.request, category='test')

        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0]['id'], 'action1')

    def test_uiaction_category_reg_fail(self):
        class Content(object):
            __name__ = ''

        ptah.uiaction(Content, 'action1', 'Action 10', category='test')
        ptah.uiaction(Content, 'action1', 'Action 11', category='test')
        self.assertRaises(ConfigurationConflictError, self.init_ptah)

    def test_uiaction_category_reg(self):
        class Content(object):
            __name__ = ''

        ptah.uiaction(Content, 'action1', 'Action 10')
        ptah.uiaction(Content, 'action1', 'Action 11', category='test')

        self.init_ptah()

        actions = ptah.list_uiactions(Content(), self.request)
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0]['title'], 'Action 10')

        actions = ptah.list_uiactions(Content(), self.request, category='test')

        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0]['title'], 'Action 11')
