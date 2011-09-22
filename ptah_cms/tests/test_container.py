import transaction
from memphis import config

import ptah
import ptah_cms

from base import Base


class Content(ptah_cms.Content):
            
    __type__ = ptah_cms.Type('content', 'Test Content')
    __uuid_generator__ = ptah.UUIDGenerator('cms+content')


class Container(ptah_cms.Container):

    __type__ = ptah_cms.Type('container', 'Test Container')
    __uuid_generator__ = ptah.UUIDGenerator('cms+container')


class TestContainer(Base):

    def test_container_basics(self):
        container = Container(__name__ = 'container', __path__ = '/container/')
        content = Content(title='Content')

        ptah_cms.Session.add(container)
        ptah_cms.Session.add(content)
        ptah_cms.Session.flush()

        self.assertEqual(content.__path__, '')

        self.assertRaises(
            ValueError, container.__setitem__, 'content', object())

        self.assertRaises(
            ValueError, container.__setitem__, 'content', container)

        container['content'] = content
        self.assertEqual(content.__name__, 'content')
        self.assertEqual(content.__path__, '/container/content/')
        self.assertEqual(content.__parent__, container)
        self.assertEqual(content.__parent_id__, container.__uuid__)

        content_uuid = content.__uuid__
        container_uuid = container.__uuid__
        transaction.commit()

        container = ptah.resolve(container_uuid)
        self.assertTrue('content' in container)
        self.assertEqual(container.keys(), ['content'])
        self.assertEqual(container['content'].__uuid__, content_uuid)
        self.assertEqual(container.get('content').__uuid__, content_uuid)
        self.assertEqual(container.get('unknown'), None)
        self.assertRaises(KeyError, container.__getitem__, 'unknown')

        content = container['content']
        self.assertRaises(
            KeyError, container.__setitem__, 'content', content)

    def test_container_simple_move(self):
        container = Container(__name__ = 'container', __path__ = '/container/')
        content = Content(title='Content')

        ptah_cms.Session.add(container)
        ptah_cms.Session.add(content)
        ptah_cms.Session.flush()

        container['content'] = content

        content_uuid = content.__uuid__
        container_uuid = container.__uuid__
        transaction.commit()

        container = ptah.resolve(container_uuid)
        content = ptah.resolve(content_uuid)

        container['moved'] = content

        self.assertEqual(content.__name__, 'moved')
        self.assertEqual(content.__path__, '/container/moved/')
        self.assertEqual(content.__parent__, container)
        self.assertEqual(content.__parent_id__, container.__uuid__)
        transaction.commit()

        container = ptah.resolve(container_uuid)
        self.assertEqual(container.keys(), ['moved'])
        self.assertEqual(container['moved'].__uuid__, content_uuid)

    def test_container_simple_move_to_subtree(self):
        container = Container(__name__ = 'container', __path__ = '/container/')
        folder = Container(title='Folder')
        content = Content(title='Content')

        ptah_cms.Session.add(container)
        ptah_cms.Session.add(folder)
        ptah_cms.Session.add(content)
        ptah_cms.Session.flush()

        container['content'] = content
        container['folder'] = folder

        content_uuid = content.__uuid__
        container_uuid = container.__uuid__
        folder_uuid = folder.__uuid__
        transaction.commit()

        container = ptah.resolve(container_uuid)
        content = ptah.resolve(content_uuid)
        folder = ptah.resolve(folder_uuid)

        self.assertEqual(container.keys(), ['folder', 'content'])

        folder['new-content'] = content

        self.assertEqual(content.__name__, 'new-content')
        self.assertEqual(content.__path__, '/container/folder/new-content/')
        self.assertEqual(content.__parent__, folder)
        self.assertEqual(content.__parent_id__, folder.__uuid__)
        transaction.commit()

        folder = ptah.resolve(folder_uuid)
        container = ptah.resolve(container_uuid)
        self.assertEqual(container.keys(), ['folder'])
        self.assertEqual(folder.keys(), ['new-content'])

    def test_container_simple_rename_subtree(self):
        container = Container(__name__ = 'container', __path__ = '/container/')
        folder1 = Container(title='Folder1')
        folder2 = Container(title='Folder2')
        content = Content(title='Content')

        ptah_cms.Session.add(container)
        ptah_cms.Session.add(folder1)
        ptah_cms.Session.add(folder2)
        ptah_cms.Session.add(content)
        ptah_cms.Session.flush()

        container['folder1'] = folder1
        folder1['folder2'] = folder2
        folder2['content'] = content

        content_uuid = content.__uuid__
        container_uuid = container.__uuid__
        folder1_uuid = folder1.__uuid__
        folder2_uuid = folder2.__uuid__
        transaction.commit()

        container = ptah.resolve(container_uuid)

        container['new-folder'] = container['folder1']
        transaction.commit()

        folder1 = ptah.resolve(folder1_uuid)
        folder2 = ptah.resolve(folder2_uuid)
        content = ptah.resolve(content_uuid)
        container = ptah.resolve(container_uuid)
        
        self.assertEqual(container.keys(), ['new-folder'])
        self.assertEqual(folder1.__path__, '/container/new-folder/')
        self.assertEqual(folder2.__path__, '/container/new-folder/folder2/')
        self.assertEqual(content.__path__,
                         '/container/new-folder/folder2/content/')
        
    def test_container_move_self_recursevly(self):
        container = Container(__name__ = 'container', __path__ = '/container/')
        folder = Container(title='Folder')

        ptah_cms.Session.add(container)
        ptah_cms.Session.add(folder)
        ptah_cms.Session.flush()

        container['folder'] = folder

        folder_uuid = folder.__uuid__
        container_uuid = container.__uuid__
        transaction.commit()

        container = ptah.resolve(container_uuid)
        folder = ptah.resolve(folder_uuid)

        self.assertRaises(
            TypeError, folder.__setitem__, 'subfolder', container)

    def test_container_delete(self):
        container = Container(__name__ = 'container', __path__ = '/container/')
        content = Content(title='Content')

        ptah_cms.Session.add(container)
        ptah_cms.Session.add(content)
        ptah_cms.Session.flush()
        
        container['content'] = content

        content_uuid = content.__uuid__
        container_uuid = container.__uuid__
        transaction.commit()

        container = ptah.resolve(container_uuid)
        del container['content']
        transaction.commit()
        
        self.assertTrue(ptah.resolve(content_uuid) is None)

        container = ptah.resolve(container_uuid)
        self.assertEqual(container.keys(), [])
        self.assertRaises(KeyError, container.__delitem__, 'content')
        self.assertRaises(KeyError, container.__delitem__, Content())

    def test_container_delete_recursive(self):
        container = Container(__name__ = 'container', __path__ = '/container/')
        folder = Container(title='Folder')
        content = Content(title='Content')

        ptah_cms.Session.add(container)
        ptah_cms.Session.add(folder)
        ptah_cms.Session.add(content)
        ptah_cms.Session.flush()

        container['folder'] = folder
        folder['content'] = content

        content_uuid = content.__uuid__
        container_uuid = container.__uuid__
        folder_uuid = folder.__uuid__
        transaction.commit()

        container = ptah.resolve(container_uuid)
        del container['folder']
        transaction.commit()

        self.assertTrue(ptah.resolve(content_uuid) is None)
        self.assertTrue(ptah.resolve(folder_uuid) is None)
