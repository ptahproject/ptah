import uuid
import transaction
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
        
        self.assertTrue('mycontent' in ptah_cms.registeredTypes)

        tinfo = ptah_cms.registeredTypes['mycontent']

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

        content = MyContent.__type__.create(title='Test content')

        self.assertTrue(isinstance(content, MyContent))
        self.assertEqual(content.title, 'Test content')

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
            MyContent.__uuid_generator__().startswith('cms+mycontent:'))

    def test_tinfo_resolver(self):
        import ptah, ptah_cms
    
        global MyContent
        class MyContent(ptah_cms.Content):
            __type__ = ptah_cms.Type('mycontent2', 'MyContent')

        self._init_memphis()
        
        content = MyContent.__type__.create(title='Test content')
        c_uuid = content.__uuid__
        ptah_cms.Session.add(content)
        transaction.commit()

        c = ptah.resolve(c_uuid)
        self.assertTrue(isinstance(c, MyContent))
