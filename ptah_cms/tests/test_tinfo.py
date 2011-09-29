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

        self.assertEqual(tinfo.__uri__, 'cms+type:mycontent')
        self.assertEqual(tinfo.name, 'mycontent')
        self.assertEqual(tinfo.title, 'MyContent')
        self.assertEqual(tinfo.factory, MyContent)

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
        self.assertTrue(content not in ptah_cms.Session)

    def test_tinfo_alchemy(self):
        import ptah_cms

        global MyContent
        class MyContent(ptah_cms.Content):
            __tablename__ = "test_mycontents"
            __type__ = ptah_cms.Type('mycontent', 'MyContent')

        self._init_memphis()

        self.assertEqual(
            MyContent.__mapper_args__['polymorphic_identity'], 
            'cms+type:mycontent')

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

    def test_tinfo_type_resolver(self):
        import ptah, ptah_cms

        global MyContent
        class MyContent(ptah_cms.Content):
            __type__ = ptah_cms.Type('mycontent2', 'MyContent')

        self._init_memphis()

        tinfo_uri = MyContent.__type__.__uri__

        self.assertEqual(tinfo_uri, 'cms+type:mycontent2')
        self.assertIs(ptah.resolve(tinfo_uri), MyContent.__type__)
