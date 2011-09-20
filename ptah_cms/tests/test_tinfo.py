import uuid
import transaction
from memphis import config

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
        self.assertEqual(tinfo.factory, MyContent)

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
