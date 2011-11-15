from ptah import config
from base import Base


class TestUIAction(Base):

    def tearDown(self):
        config.cleanup_system(self.__class__.__module__)
        super(TestUIAction, self).tearDown()

    def _setup_ptah(self):
        pass

    def test_uiaction(self):
        import ptah.cms

        class Content(object):
            __name__ = ''

        ptah.cms.uiaction(Content, 'action1', 'Action 1')
        self._init_ptah()

        request = self._makeRequest()

        actions = ptah.cms.list_uiactions(Content(), request)

        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0]['id'], 'action1')

    def test_uiaction_conflicts(self):
        import ptah.cms

        class Content(object):
            __name__ = ''

        ptah.cms.uiaction(Content, 'action1', 'Action 1')
        ptah.cms.uiaction(Content, 'action1', 'Action 1')
        self.assertRaises(config.ConflictError, self._init_ptah)

    def test_uiaction_url(self):
        import ptah.cms

        class Content(object):
            __name__ = ''

        ptah.cms.uiaction(Content, 'action1', 'Action 1',
                          action='test.html')
        self._init_ptah()
        request = self._makeRequest()

        actions = ptah.cms.list_uiactions(Content(), request)
        self.assertEqual(actions[0]['url'], 'http://localhost:8080/test.html')

    def test_uiaction_absolute_url(self):
        import ptah.cms

        class Content(object):
            __name__ = ''

        ptah.cms.uiaction(Content, 'action1', 'Action 1',
                          action='/content/about.html')
        self._init_ptah()
        request = self._makeRequest()

        actions = ptah.cms.list_uiactions(Content(), request)
        self.assertEqual(actions[0]['url'],
                         'http://localhost:8080/content/about.html')

    def test_uiaction_custom_url(self):
        import ptah.cms

        class Content(object):
            __name__ = ''

        def customAction(content, request):
            return 'http://github.com/ptahproject'

        ptah.cms.uiaction(Content, 'action1', 'Action 1',
                          action=customAction)
        self._init_ptah()
        request = self._makeRequest()

        actions = ptah.cms.list_uiactions(Content(), request)
        self.assertEqual(actions[0]['url'], 'http://github.com/ptahproject')

    def test_uiaction_condition(self):
        import ptah.cms

        class Content(object):
            __name__ = ''

        allow = False
        def condition(content, request):
            return allow

        ptah.cms.uiaction(
            Content, 'action1', 'Action 1',
            action='test.html', condition=condition)
        self._init_ptah()
        request = self._makeRequest()

        actions = ptah.cms.list_uiactions(Content(), request)
        self.assertEqual(len(actions), 0)

        allow = True
        actions = ptah.cms.list_uiactions(Content(), request)
        self.assertEqual(len(actions), 1)

    def test_uiaction_permission(self):
        import ptah, ptah.cms

        class Content(object):
            __name__ = ''

        allow = False
        def check_permission(permission, content, request=None, throw=False):
            return allow

        ptah.cms.uiaction(
            Content, 'action1', 'Action 1', permission='View')
        self._init_ptah()
        request = self._makeRequest()

        orig_cp = ptah.check_permission
        ptah.check_permission = check_permission

        actions = ptah.cms.list_uiactions(Content(), request)
        self.assertEqual(len(actions), 0)

        allow = True
        actions = ptah.cms.list_uiactions(Content(), request)
        self.assertEqual(len(actions), 1)

        ptah.check_permission = orig_cp

    def test_uiaction_sort_weight(self):
        import ptah.cms

        class Content(object):
            __name__ = ''

        ptah.cms.uiaction(Content, 'view', 'View', sort_weight=1.0)
        ptah.cms.uiaction(Content, 'action', 'Action', sort_weight=2.0)
        self._init_ptah()

        request = self._makeRequest()

        actions = ptah.cms.list_uiactions(Content(), request)

        self.assertEqual(actions[0]['id'], 'view')
        self.assertEqual(actions[1]['id'], 'action')

    def test_uiaction_userdata(self):
        import ptah.cms

        class Content(object):
            __name__ = ''

        ptah.cms.uiaction(Content, 'view', 'View', testinfo='test')
        self._init_ptah()

        request = self._makeRequest()

        actions = ptah.cms.list_uiactions(Content(), request)

        self.assertEqual(actions[0]['data'], {'testinfo': 'test'})
