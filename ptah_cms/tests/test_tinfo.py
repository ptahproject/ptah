import transaction
import sqlalchemy as sqla
from memphis import config, form
from pyramid.httpexceptions import HTTPForbidden

from base import Base


class TestTypeInfo(Base):

    def tearDown(self):
        config.cleanup_system(self.__class__.__module__)
        super(TestTypeInfo, self).tearDown()

    def _setup_memphis(self):
        pass

    def test_tinfo(self):
        import ptah_cms

        global MyContent
        class MyContent(ptah_cms.Content):

            __type__ = ptah_cms.Type('mycontent', 'MyContent')

        self._init_memphis()

        self.assertTrue('cms+type:mycontent' in ptah_cms.Types)

        tinfo = ptah_cms.Types['cms+type:mycontent']

        self.assertEqual(tinfo.__uri__, 'cms+type:mycontent')
        self.assertEqual(tinfo.name, 'mycontent')
        self.assertEqual(tinfo.title, 'MyContent')
        self.assertEqual(tinfo.cls, MyContent)

    def test_tinfo_title(self):
        import ptah_cms

        class MyContent(ptah_cms.Content):
            __type__ = ptah_cms.Type('mycontent')

        self.assertEqual(MyContent.__type__.title, 'Mycontent')

        class MyContent(ptah_cms.Content):
            __type__ = ptah_cms.Type('mycontent', 'MyContent')

        self.assertEqual(MyContent.__type__.title, 'MyContent')

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

    def test_tinfo_global_allow_Node(self):
        import ptah_cms

        global MyContent
        class MyContent(ptah_cms.Node):
            __type__ = ptah_cms.Type('mycontent', 'Content', permission=None)
        class MyContainer(ptah_cms.Node):
            __type__ = ptah_cms.Type('mycontainer', 'Container',
                                     global_allow = True)
        self._init_memphis()

        self.assertFalse(MyContent.__type__.global_allow)
        self.assertTrue(MyContainer.__type__.global_allow)

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

        content = ptah_cms.Types['cms+type:mycontent'].create(title='Test content')

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

    def test_tinfo_fieldset(self):
        import ptah, ptah_cms

        MySchema = ptah_cms.ContentSchema + \
            form.Fieldset(form.TextField('test'))

        class MyContent(ptah_cms.Content):
            __type__ = ptah_cms.Type('mycontent2', 'MyContent',
                                     fieldset=MySchema)

        tinfo = MyContent.__type__
        self.assertIs(tinfo.fieldset, MySchema)

    def test_tinfo_fieldset_gen(self):
        import ptah, ptah_cms

        global MyContent
        class MyContent(ptah_cms.Content):
            __tablename__ = 'test_content'
            __type__ = ptah_cms.Type('mycontent2', 'MyContent')

            test = sqla.Column(sqla.Unicode())

        self._init_memphis()

        tinfo = MyContent.__type__
        self.assertIn('test', tinfo.fieldset)
        self.assertIn('title', tinfo.fieldset)
        self.assertIn('description', tinfo.fieldset)
        self.assertNotIn('__owner__', tinfo.fieldset)
        self.assertEqual(len(tinfo.fieldset), 3)

    def test_tinfo_type_resolver(self):
        import ptah, ptah_cms

        global MyContent
        class MyContent(ptah_cms.Content):
            __type__ = ptah_cms.Type('mycontent2', 'MyContent')

        self._init_memphis()

        tinfo_uri = MyContent.__type__.__uri__

        self.assertEqual(tinfo_uri, 'cms+type:mycontent2')
        self.assertIs(ptah.resolve(tinfo_uri), MyContent.__type__)

    def test_names_filter(self):
        from ptah_cms.tinfo import namesFilter

        self.assertFalse(namesFilter('_test'))
        self.assertFalse(namesFilter('__test__'))
        self.assertTrue(namesFilter('__test__', ('__test__',)))

        excludeNames = ('expires', 'contributors', 'creators',
                        'view', 'subjects',
                        'publisher', 'effective', 'created', 'modified')
        for name in excludeNames:
            self.assertFalse(namesFilter(name))
            self.assertTrue(namesFilter(name, (name,)))
