import transaction

import ptah
from ptah.testing import PtahTestCase


class TestContainer(PtahTestCase):

    def setUp(self):
        global TestCMSContent, TestCMSContainer
        class TestCMSContent(ptah.cms.Content):
            __type__ = ptah.cms.Type('content', 'Test Content')
            __uri_factory__ = ptah.UriFactory('cms-content')

        class TestCMSContainer(ptah.cms.Container):
            __type__ = ptah.cms.Type('container', 'Test Container')
            __uri_factory__ = ptah.UriFactory('cms-container')

        self.Content = TestCMSContent
        self.Container = TestCMSContainer

        super(TestContainer, self).setUp()

    def test_container_basics(self):
        container = self.Container(
            __name__ = 'container', __path__ = '/container/')
        content = self.Content(title='Content')

        Session = ptah.get_session()
        Session.add(container)
        Session.add(content)
        Session.flush()

        self.assertEqual(content.__path__, '')

        self.assertRaises(
            ValueError, container.__setitem__, 'content', object())

        self.assertRaises(
            ValueError, container.__setitem__, 'content', container)

        container['content'] = content
        self.assertEqual(content.__name__, 'content')
        self.assertEqual(content.__path__, '/container/content/')
        self.assertEqual(content.__parent__, container)
        self.assertEqual(content.__parent_uri__, container.__uri__)

        content_uri = content.__uri__
        container_uri = container.__uri__
        transaction.commit()

        container = ptah.resolve(container_uri)
        self.assertTrue('content' in container)
        self.assertEqual(container.keys(), ['content'])
        self.assertEqual(container['content'].__uri__, content_uri)
        self.assertEqual(container.get('content').__uri__, content_uri)
        self.assertEqual(container.get('unknown'), None)
        self.assertRaises(KeyError, container.__getitem__, 'unknown')

        content = container['content']
        self.assertRaises(
            KeyError, container.__setitem__, 'content', content)

    def test_container_keys_values_del(self):
        container = self.Container(
            __name__ = 'container', __path__ = '/container/')
        content = self.Content(title='Content')

        container['content'] = content
        self.assertEqual(container.keys(), ['content'])
        self.assertEqual(list(container.values()), [content])

        del container['content']
        self.assertEqual(container.keys(), [])
        self.assertEqual(container.values(), [])

    def test_container_keys_with_local(self):
        container = self.Container(__name__ = 'container',
                                   __path__ = '/container/')
        content = self.Content(title='Content')
        container['content'] = content

        Session = ptah.get_session()
        Session.add(container)
        Session.add(content)
        Session.flush()

        content_uri = content.__uri__
        container_uri = container.__uri__
        transaction.commit()

        container = ptah.resolve(container_uri)

        c2 = self.Content(title='Content2')
        container['content2'] = c2

        self.assertEqual(container.keys(), ['content', 'content2'])
        self.assertEqual([c.__uri__ for c in container.values()],
                         [content_uri, c2.__uri__])

        del container['content']

        self.assertEqual(container.keys(), ['content2'])
        self.assertEqual([c.__uri__ for c in container.values()],
                         [c2.__uri__])

    def test_container_simple_move(self):
        container = self.Container(__name__ = 'container',
                                   __path__ = '/container/')
        content = self.Content(title='Content')

        Session = ptah.get_session()
        Session.add(container)
        Session.add(content)
        Session.flush()

        container['content'] = content

        content_uri = content.__uri__
        container_uri = container.__uri__
        transaction.commit()

        container = ptah.resolve(container_uri)
        content = ptah.resolve(content_uri)

        container['moved'] = content

        self.assertEqual(content.__name__, 'moved')
        self.assertEqual(content.__path__, '/container/moved/')
        self.assertEqual(content.__parent__, container)
        self.assertEqual(content.__parent_uri__, container.__uri__)
        transaction.commit()

        container = ptah.resolve(container_uri)
        self.assertEqual(container.keys(), ['moved'])
        self.assertEqual(container['moved'].__uri__, content_uri)

    def test_container_getitem(self):
        container = self.Container(__name__ = 'container',
                                   __path__ = '/container/')
        content1 = self.Content(title='Content1')
        content2 = self.Content(title='Content2')

        container['content1'] = content1
        container['content2'] = content2

        self.assertEqual(container['content1'].__uri__, content1.__uri__)
        self.assertEqual(container['content2'].__uri__, content2.__uri__)
        self.assertEqual(container.get('content1').__uri__, content1.__uri__)
        self.assertEqual(container.get('content2').__uri__, content2.__uri__)

        Session = ptah.get_session()
        Session.add(container)
        Session.add(content1)
        Session.add(content2)
        Session.flush()

        c_u = container.__uri__
        c1_u = content1.__uri__
        c2_u = content2.__uri__
        transaction.commit()

        container = ptah.resolve(c_u)
        self.assertEqual(container['content1'].__uri__, c1_u)
        self.assertEqual(container['content2'].__uri__, c2_u)
        transaction.commit()

        container = ptah.resolve(c_u)
        self.assertEqual(container.get('content1').__uri__, c1_u)
        self.assertEqual(container.get('content2').__uri__, c2_u)

    def test_container_items(self):
        container = self.Container(__name__ = 'container',
                                   __path__ = '/container/')
        content1 = self.Content(title='Content1')
        content2 = self.Content(title='Content2')

        container['content1'] = content1
        container['content2'] = content2

        self.assertEqual(list(container.items()),
                         [('content1', content1), ('content2', content2)])

    def test_container_simple_move_to_subtree(self):
        container = self.Container(__name__ = 'container',
                                   __path__ = '/container/')
        folder = self.Container(title='Folder')
        content = self.Content(title='Content')

        Session = ptah.get_session()
        Session.add(container)
        Session.add(folder)
        Session.add(content)
        Session.flush()

        container['content'] = content
        container['folder'] = folder

        content_uri = content.__uri__
        container_uri = container.__uri__
        folder_uri = folder.__uri__
        transaction.commit()

        container = ptah.resolve(container_uri)
        content = ptah.resolve(content_uri)
        folder = ptah.resolve(folder_uri)

        self.assertEqual(container.keys(), ['folder', 'content'])

        folder['new-content'] = content

        self.assertEqual(content.__name__, 'new-content')
        self.assertEqual(content.__path__, '/container/folder/new-content/')
        self.assertEqual(content.__parent__, folder)
        self.assertEqual(content.__parent_uri__, folder.__uri__)
        transaction.commit()

        folder = ptah.resolve(folder_uri)
        container = ptah.resolve(container_uri)
        self.assertEqual(container.keys(), ['folder'])
        self.assertEqual(folder.keys(), ['new-content'])

    def test_container_insert_subtree(self):
        container = self.Container(__name__ = 'container',
                                   __path__ = '/container/')
        folder = self.Container(title='Folder')
        content = self.Content(title='Content')

        Session = ptah.get_session()
        Session.add(container)
        Session.add(folder)
        Session.add(content)

        folder['content'] = content
        container['folder'] = folder

        content_uri = content.__uri__
        folder_uri = folder.__uri__
        container_uri = container.__uri__
        transaction.commit()

        container = ptah.resolve(container_uri)
        content = ptah.resolve(content_uri)
        folder = ptah.resolve(folder_uri)

        self.assertEqual(container.keys(), ['folder'])
        self.assertEqual(folder.keys(), ['content'])
        self.assertEqual(folder.__path__, '/container/folder/')
        self.assertEqual(content.__path__, '/container/folder/content/')
        transaction.commit()

    def test_container_simple_rename_subtree(self):
        container = self.Container(__name__ = 'container',
                                   __path__ = '/container/')
        folder1 = self.Container(title='Folder1')
        folder2 = self.Container(title='Folder2')
        content = self.Content(title='Content')

        Session = ptah.get_session()
        Session.add(container)
        Session.add(folder1)
        Session.add(folder2)
        Session.add(content)
        Session.flush()

        container['folder1'] = folder1
        folder1['folder2'] = folder2
        folder2['content'] = content

        content_uri = content.__uri__
        container_uri = container.__uri__
        folder1_uri = folder1.__uri__
        folder2_uri = folder2.__uri__
        transaction.commit()

        container = ptah.resolve(container_uri)

        container['new-folder'] = container['folder1']
        transaction.commit()

        folder1 = ptah.resolve(folder1_uri)
        folder2 = ptah.resolve(folder2_uri)
        content = ptah.resolve(content_uri)
        container = ptah.resolve(container_uri)

        self.assertEqual(container.keys(), ['new-folder'])
        self.assertEqual(folder1.__path__, '/container/new-folder/')
        self.assertEqual(folder2.__path__, '/container/new-folder/folder2/')
        self.assertEqual(content.__path__,
                         '/container/new-folder/folder2/content/')

    def test_container_move_self_recursevly(self):
        container = self.Container(__name__ = 'container',
                                   __path__ = '/container/')
        folder = self.Container(title='Folder')

        Session = ptah.get_session()
        Session.add(container)
        Session.add(folder)
        Session.flush()

        container['folder'] = folder

        folder_uri = folder.__uri__
        container_uri = container.__uri__
        transaction.commit()

        container = ptah.resolve(container_uri)
        folder = ptah.resolve(folder_uri)

        self.assertRaises(
            TypeError, folder.__setitem__, 'subfolder', container)

    def test_container_delete(self):
        container = self.Container(__name__ = 'container',
                                   __path__ = '/container/')
        content = self.Content(title='Content')

        Session = ptah.get_session()
        Session.add(container)
        Session.add(content)
        Session.flush()

        container['content'] = content

        content_uri = content.__uri__
        container_uri = container.__uri__
        transaction.commit()

        container = ptah.resolve(container_uri)
        del container['content']
        self.assertEqual(container.keys(), [])
        self.assertEqual(container.values(), [])

        transaction.commit()

        self.assertTrue(ptah.resolve(content_uri) is None)

        container = ptah.resolve(container_uri)
        self.assertEqual(container.keys(), [])
        self.assertRaises(KeyError, container.__delitem__, 'content')
        self.assertRaises(KeyError, container.__delitem__, self.Content())

    def test_container_delete_recursive(self):
        container = self.Container(__name__='container', __path__='/container/')
        folder = self.Container(title='Folder')
        content = self.Content(title='Content')

        Session = ptah.get_session()
        Session.add(container)
        Session.add(folder)
        Session.add(content)
        Session.flush()

        container['folder'] = folder
        folder['content'] = content

        content_uri = content.__uri__
        container_uri = container.__uri__
        folder_uri = folder.__uri__
        transaction.commit()

        container = ptah.resolve(container_uri)
        del container['folder']
        transaction.commit()

        self.assertTrue(ptah.resolve(content_uri) is None)
        self.assertTrue(ptah.resolve(folder_uri) is None)

    def test_container_setitem_parent_not_node(self):
        container = self.Container(__name__='container', __path__='/container/')
        content = self.Content(title='Content')

        container.__parent__ = object()

        # this line should not fail
        container['content'] = content

        self.assertIs(container['content'], content)

    def test_container_create(self):
        container = self.Container(__name__='container', __path__='/container/')

        self.assertRaises(
            ptah.cms.NotFound, container.create, 'unknown', 'test')

        tinfo = self.Content.__type__
        tname = tinfo.__uri__

        self.assertRaises(
            ptah.cms.Forbidden, container.create, tname, 'test')

        tinfo.permission = None

        self.assertRaises(
            ptah.cms.Error, container.create, tname, 'te/st')

        self.assertRaises(
            ptah.cms.Error, container.create, tname, ' test')

        content = container.create(tname, 'test', title = 'Test title')
        self.assertIsInstance(content, self.Content)
        self.assertIsNotNone(content.created)
        self.assertIsNotNone(content.modified)
        self.assertEqual(content.title, 'Test title')
        self.assertEqual(container.keys(), ['test'])

        self.assertRaises(
            ptah.cms.Error, container.create,
            tname, 'test', title = 'Test title')

        tinfo.permission = ptah.NOT_ALLOWED

    def test_container_info(self):
        container = self.Container(__name__='container', __path__='/container/')

        info = container.info()
        self.assertEqual(info['__name__'], 'container')
        self.assertTrue(info['__container__'])
