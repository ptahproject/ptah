import colander
import transaction
from zope import interface
from memphis import config
from pyramid.httpexceptions import HTTPForbidden

from base import Base


class TestUIAction(Base):

    def tearDown(self):
        config.cleanUp(self.__class__.__module__)
        super(TestUIAction, self).tearDown()

    def _setup_memphis(self):
        pass

    def test_uiaction(self):
        import ptah_app

        class Content(object):
            __name__ = ''

        ptah_app.uiAction(Content, 'action1', 'Action 1')
        self._init_memphis()

        request = self._makeRequest()

        actions = ptah_app.listUIActions(Content(), request)

        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0]['id'], 'action1')

    def test_uiaction_conflicts(self):
        import ptah_app

        class Content(object):
            __name__ = ''

        ptah_app.uiAction(Content, 'action1', 'Action 1')
        ptah_app.uiAction(Content, 'action1', 'Action 1')
        self.assertRaises(config.ConflictError, self._init_memphis)

    def test_uiaction_url(self):
        import ptah_app

        class Content(object):
            __name__ = ''

        ptah_app.uiAction(Content, 'action1', 'Action 1',
                               action='test.html')
        self._init_memphis()
        request = self._makeRequest()

        actions = ptah_app.listUIActions(Content(), request)
        self.assertEqual(actions[0]['url'], 'http://localhost:8080/test.html')

    def test_uiaction_absolute_url(self):
        import ptah_app

        class Content(object):
            __name__ = ''

        ptah_app.uiAction(Content, 'action1', 'Action 1',
                               action='/content/about.html')
        self._init_memphis()
        request = self._makeRequest()

        actions = ptah_app.listUIActions(Content(), request)
        self.assertEqual(actions[0]['url'],
                         'http://localhost:8080/content/about.html')

    def test_uiaction_custom_url(self):
        import ptah_app

        class Content(object):
            __name__ = ''

        def customAction(content, request):
            return 'http://github.com/ptahproject'

        ptah_app.uiAction(Content, 'action1', 'Action 1',
                               action=customAction)
        self._init_memphis()
        request = self._makeRequest()

        actions = ptah_app.listUIActions(Content(), request)
        self.assertEqual(actions[0]['url'], 'http://github.com/ptahproject')

    def test_uiaction_condition(self):
        import ptah_app

        class Content(object):
            __name__ = ''

        allow = False
        def condition(content, request):
            return allow

        ptah_app.uiAction(
            Content, 'action1', 'Action 1',
            action='test.html', condition=condition)
        self._init_memphis()
        request = self._makeRequest()

        actions = ptah_app.listUIActions(Content(), request)
        self.assertEqual(len(actions), 0)

        allow = True
        actions = ptah_app.listUIActions(Content(), request)
        self.assertEqual(len(actions), 1)

    def test_uiaction_permission(self):
        import ptah, ptah_app

        class Content(object):
            __name__ = ''

        allow = False
        def checkPermission(permission, content, request=None, throw=False):
            return allow

        ptah_app.uiAction(
            Content, 'action1', 'Action 1', permission='View')
        self._init_memphis()
        request = self._makeRequest()

        orig_cp = ptah.checkPermission
        ptah.checkPermission = checkPermission

        actions = ptah_app.listUIActions(Content(), request)
        self.assertEqual(len(actions), 0)

        allow = True
        actions = ptah_app.listUIActions(Content(), request)
        self.assertEqual(len(actions), 1)

        ptah.checkPermission = orig_cp

    def test_uiaction_sort_weight(self):
        import ptah_app

        class Content(object):
            __name__ = ''

        ptah_app.uiAction(Content, 'view', 'View', sortWeight=1.0)
        ptah_app.uiAction(Content, 'action', 'Action', sortWeight=2.0)
        self._init_memphis()

        request = self._makeRequest()

        actions = ptah_app.listUIActions(Content(), request)

        self.assertEqual(actions[0]['id'], 'view')
        self.assertEqual(actions[1]['id'], 'action')

    def test_uiaction_userdata(self):
        import ptah_app

        class Content(object):
            __name__ = ''

        ptah_app.uiAction(Content, 'view', 'View', testinfo='test')
        self._init_memphis()

        request = self._makeRequest()

        actions = ptah_app.listUIActions(Content(), request)

        self.assertEqual(actions[0]['data'], {'testinfo': 'test'})
