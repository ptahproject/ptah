import colander
import transaction
from zope import interface
from memphis import config
from pyramid.httpexceptions import HTTPForbidden

from base import Base


class TestTypeInfo(Base):

    def tearDown(self):
        config.cleanUp(self.__class__.__module__)
        super(TestTypeInfo, self).tearDown()

    def _setup_memphis(self):
        pass

    def test_tinfo(self):
        import ptah_cms

        global MyContent
        class MyContent(ptah_cms.Content):

            __type__ = ptah_cms.Type('mycontent', 'MyContent')

        self._init_memphis()

        self.assertTrue('mycontent' in ptah_cms.Types)

        tinfo = ptah_cms.Types['mycontent']

        self.assertEqual(tinfo.name, 'mycontent')
        self.assertEqual(tinfo.title, 'MyContent')
        self.assertEqual(tinfo.klass, MyContent)

    def test_tinfo_checks(self):
        import ptah_cms

        global MyContent, MyContainer
        class MyContent(ptah_cms.Content):
            __type__ = ptah_cms.Type('mycontent', 'Content', permission=None)
        class MyContainer(ptah_cms.Container):
            __type__ = ptah_cms.Type('mycontainer', 'Container')
        self._init_memphis()

        content = MyContent()
        container = MyContainer()

        # always fail
        self.assertFalse(MyContent.__type__.isAllowed(content))
        self.assertRaises(
            HTTPForbidden, MyContent.__type__.checkContext, content)

        #
        self.assertTrue(MyContent.__type__.isAllowed(container))
        self.assertEqual(MyContent.__type__.checkContext(container), None)

        # permission
        MyContent.__type__.permission = 'Protected'
        self.assertFalse(MyContent.__type__.isAllowed(container))
        self.assertRaises(
            HTTPForbidden, MyContent.__type__.checkContext, container)

    def test_tinfo_list(self):
        import ptah_cms

        global MyContent, MyContainer
        class MyContent(ptah_cms.Content):
            __type__ = ptah_cms.Type('mycontent', 'Content', permission=None)
        class MyContainer(ptah_cms.Container):
            __type__ = ptah_cms.Type('mycontainer', 'Container')
        self._init_memphis()

        content = MyContent()
        container = MyContainer()

        self.assertEqual(MyContent.__type__.listTypes(content), ())
        self.assertEqual(MyContent.__type__.listTypes(container), ())

        self.assertEqual(MyContainer.__type__.listTypes(container),
                         [MyContent.__type__])

        MyContent.__type__.global_allow = False
        self.assertEqual(MyContainer.__type__.listTypes(container), [])

        MyContent.__type__.global_allow = True
        MyContent.__type__.permission = 'Protected'
        self.assertEqual(MyContainer.__type__.listTypes(container), [])

    def test_tinfo_list_filtered(self):
        import ptah_cms

        global MyContent, MyContainer
        class MyContent(ptah_cms.Content):
            __type__ = ptah_cms.Type('mycontent', 'Content', permission=None)
        class MyContainer(ptah_cms.Container):
            __type__ = ptah_cms.Type(
                'mycontainer', 'Container', filter_content_types=True)

        self._init_memphis()

        content = MyContent()
        container = MyContainer()
        self.assertEqual(MyContainer.__type__.listTypes(container), [])

        MyContainer.__type__.allowed_content_types = ('mycontent',)
        self.assertEqual(MyContainer.__type__.listTypes(container),
                         [MyContent.__type__])

    def test_tinfo_conflicts(self):
        import ptah_cms

        global MyContent
        class MyContent(ptah_cms.Content):
            __type__ = ptah_cms.Type('mycontent2', 'MyContent')
        class MyContent2(ptah_cms.Content):
            __type__ = ptah_cms.Type('mycontent2', 'MyContent')

        self.assertRaises(
            config.ConflictError, self._init_memphis)

    def test_tinfo_create(self):
        import ptah_cms

        global MyContent
        class MyContent(ptah_cms.Content):
            __type__ = ptah_cms.Type('mycontent', 'MyContent')

        self._init_memphis()

        content = ptah_cms.Types['mycontent'].create(title='Test content')

        self.assertTrue(isinstance(content, MyContent))
        self.assertEqual(content.title, 'Test content')
        self.assertTrue(content in ptah_cms.Session)

    def test_tinfo_alchemy(self):
        import ptah_cms

        global MyContent
        class MyContent(ptah_cms.Content):
            __tablename__ = "test_mycontents"
            __type__ = ptah_cms.Type('mycontent', 'MyContent')

        self._init_memphis()

        self.assertEqual(
            MyContent.__mapper_args__['polymorphic_identity'], 'mycontent')
        self.assertTrue(
            MyContent.__uri_generator__().startswith('cms+mycontent:'))

    def test_tinfo_resolver(self):
        import ptah, ptah_cms

        global MyContent
        class MyContent(ptah_cms.Content):
            __type__ = ptah_cms.Type('mycontent2', 'MyContent')

        self._init_memphis()

        content = MyContent.__type__.create(title='Test content')
        c_uri = content.__uri__
        ptah_cms.Session.add(content)
        transaction.commit()

        c = ptah.resolve(c_uri)
        self.assertTrue(isinstance(c, MyContent))

    def test_tinfo_schema(self):
        import ptah, ptah_cms

        class MySchema(ptah_cms.ContentSchema):
            test = colander.SchemaNode(
                colander.Str())

        class MyContent(ptah_cms.Content):
            __type__ = ptah_cms.Type('mycontent2', 'MyContent',
                                     schema=MySchema)

        tinfo = MyContent.__type__

        self.assertFalse(isinstance(tinfo.schema, colander._SchemaMeta))


class TestAction(Base):

    def tearDown(self):
        config.cleanUp(self.__class__.__module__)
        super(TestAction, self).tearDown()

    def _setup_memphis(self):
        pass

    def test_action(self):
        import ptah_cms

        class Content(object):
            __name__ = ''

        ptah_cms.contentAction(Content, 'action1', 'Action 1')
        self._init_memphis()

        request = self._makeRequest()

        actions = ptah_cms.listActions(Content(), request)

        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0]['id'], 'action1')

    def test_action_conflicts(self):
        import ptah_cms

        class Content(object):
            __name__ = ''

        ptah_cms.contentAction(Content, 'action1', 'Action 1')
        ptah_cms.contentAction(Content, 'action1', 'Action 1')
        self.assertRaises(config.ConflictError, self._init_memphis)

    def test_action_url(self):
        import ptah_cms

        class Content(object):
            __name__ = ''

        ptah_cms.contentAction(Content, 'action1', 'Action 1',
                               action='test.html')
        self._init_memphis()
        request = self._makeRequest()

        actions = ptah_cms.listActions(Content(), request)
        self.assertEqual(actions[0]['url'], 'http://localhost:8080/test.html')

    def test_action_absolute_url(self):
        import ptah_cms

        class Content(object):
            __name__ = ''

        ptah_cms.contentAction(Content, 'action1', 'Action 1',
                               action='/content/about.html')
        self._init_memphis()
        request = self._makeRequest()

        actions = ptah_cms.listActions(Content(), request)
        self.assertEqual(actions[0]['url'],
                         'http://localhost:8080/content/about.html')

    def test_action_custom_url(self):
        import ptah_cms

        class Content(object):
            __name__ = ''

        def customAction(content, request):
            return 'http://github.com/ptahproject'

        ptah_cms.contentAction(Content, 'action1', 'Action 1',
                               action=customAction)
        self._init_memphis()
        request = self._makeRequest()

        actions = ptah_cms.listActions(Content(), request)
        self.assertEqual(actions[0]['url'], 'http://github.com/ptahproject')

    def test_action_condition(self):
        import ptah_cms

        class Content(object):
            __name__ = ''

        allow = False
        def condition(content, request):
            return allow

        ptah_cms.contentAction(
            Content, 'action1', 'Action 1',
            action='test.html', condition=condition)
        self._init_memphis()
        request = self._makeRequest()

        actions = ptah_cms.listActions(Content(), request)
        self.assertEqual(len(actions), 0)

        allow = True
        actions = ptah_cms.listActions(Content(), request)
        self.assertEqual(len(actions), 1)

    def test_action_permission(self):
        import ptah, ptah_cms

        class Content(object):
            __name__ = ''

        allow = False
        def checkPermission(permission, content, request=None, throw=False):
            return allow

        ptah_cms.contentAction(
            Content, 'action1', 'Action 1', permission='View')
        self._init_memphis()
        request = self._makeRequest()

        orig_cp = ptah.checkPermission
        ptah.checkPermission = checkPermission

        actions = ptah_cms.listActions(Content(), request)
        self.assertEqual(len(actions), 0)

        allow = True
        actions = ptah_cms.listActions(Content(), request)
        self.assertEqual(len(actions), 1)

        ptah.checkPermission = orig_cp

    def test_action_sort_weight(self):
        import ptah_cms

        class Content(object):
            __name__ = ''

        ptah_cms.contentAction(Content, 'view', 'View', sortWeight=1.0)
        ptah_cms.contentAction(Content, 'action', 'Action', sortWeight=2.0)
        self._init_memphis()

        request = self._makeRequest()

        actions = ptah_cms.listActions(Content(), request)

        self.assertEqual(actions[0]['id'], 'view')
        self.assertEqual(actions[1]['id'], 'action')

    def test_action_userdata(self):
        import ptah_cms

        class Content(object):
            __name__ = ''

        ptah_cms.contentAction(Content, 'view', 'View', testinfo='test')
        self._init_memphis()

        request = self._makeRequest()

        actions = ptah_cms.listActions(Content(), request)

        self.assertEqual(actions[0]['data'], {'testinfo': 'test'})
