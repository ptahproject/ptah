import transaction
from pyramid.interfaces import ITraverser

import ptah
from ptah import config

from base import Base


class ApplicationRoot(ptah.cms.ApplicationRoot):

    __type__ = ptah.cms.Type('traverserapp')


class TestTraverser(Base):

    def tearDown(self):
        config.cleanup_system(self.__class__.__module__)
        super(TestTraverser, self).tearDown()

    def _create_content(self):
        import ptah.cms

        factory = ptah.cms.ApplicationFactory(
            ApplicationRoot, '/test', 'root', 'Root App')
        self.factory = factory

        class MyContent(ptah.cms.Content):
            __mapper_args__ = {'polymorphic_identity': 'mycontent'}
            __uri_factory__ = ptah.UriFactory('test')

        root = factory()

        folder = MyContent(
            __name__ = 'folder',
            __parent__ = root,
            __path__ = '%sfolder/'%root.__path__)
        self.folder_uri = folder.__uri__

        content = MyContent(
            __name__ = 'content',
            __parent__ = folder,
            __path__ = '%scontent/'%folder.__path__)
        self.content_uri = content.__uri__

        ptah.cms.Session.add(folder)
        ptah.cms.Session.add(content)
        transaction.commit()

    def test_traverser_root_view(self):
        import ptah.cms
        from ptah.cms.traverser import ContentTraverser

        self._create_content()

        request = self._makeRequest(
            {'PATH_INFO': '/test/index.html'})

        root = self.factory(request)

        traverser = ITraverser(root)

        self.assertTrue(isinstance(traverser, ContentTraverser))

        info = traverser(request)
        self.assertTrue(info['context'] is root)
        self.assertEqual(info['view_name'], 'index.html')

    def test_traverser_default_root(self):
        import ptah.cms

        request = self._makeRequest(
            {'PATH_INFO': '/test/index.html',
             'bfg.routes.route': {}})

        factory = ptah.cms.ApplicationFactory(
            ApplicationRoot, '', 'root', 'Root App')
        root = factory(request)

        traverser = ITraverser(root)

        info = traverser(request)
        self.assertTrue(info['context'] is root)
        self.assertEqual(info['view_name'], 'test')

    def test_traverser_root_no_view(self):
        self._create_content()

        request = self._makeRequest({'PATH_INFO': '/test/'})

        root = self.factory(request)
        traverser = ITraverser(root)

        info = traverser(request)
        self.assertTrue(info['context'] is root)
        self.assertEqual(info['view_name'], '')

    def test_traverser_folder(self):
        self._create_content()

        request = self._makeRequest({'PATH_INFO': '/test/folder'})

        root = self.factory(request)
        traverser = ITraverser(root)

        info = traverser(request)
        self.assertEqual(info['context'].__uri__, self.folder_uri)
        self.assertEqual(info['view_name'], '')
        self.assertEqual(info['traversed'], ('folder',))

    def test_traverser_folder_2(self):
        self._create_content()

        request = self._makeRequest({'PATH_INFO': '/test/folder/'})

        root = self.factory(request)
        traverser = ITraverser(root)

        info = traverser(request)
        self.assertEqual(info['context'].__uri__, self.folder_uri)
        self.assertEqual(info['view_name'], '')
        self.assertEqual(info['traversed'], ('folder',))

    def test_traverser_folder_view(self):
        self._create_content()

        request = self._makeRequest({'PATH_INFO': '/test/folder/index.html'})

        root = self.factory(request)
        traverser = ITraverser(root)

        info = traverser(request)
        self.assertEqual(info['context'].__uri__, self.folder_uri)
        self.assertEqual(info['view_name'], 'index.html')
        self.assertEqual(info['traversed'], ('folder',))

    def test_traverser_folder_subcontent1(self):
        self._create_content()

        request = self._makeRequest({'PATH_INFO': '/test/folder/content'})

        root = self.factory(request)
        traverser = ITraverser(root)

        info = traverser(request)
        self.assertEqual(info['context'].__uri__, self.content_uri)
        self.assertEqual(info['view_name'], '')
        self.assertEqual(info['traversed'], ('folder','content'))

    def test_traverser_folder_subcontent2(self):
        self._create_content()

        request = self._makeRequest({'PATH_INFO': '/test/folder/content/'})

        root = self.factory(request)
        traverser = ITraverser(root)

        info = traverser(request)
        self.assertEqual(info['context'].__uri__, self.content_uri)
        self.assertEqual(info['view_name'], '')
        self.assertEqual(info['traversed'], ('folder','content'))

    def test_traverser_folder_subcontent_view(self):
        self._create_content()

        request = self._makeRequest(
            {'PATH_INFO': '/test/folder/content/index.html'})

        root = self.factory(request)
        traverser = ITraverser(root)

        info = traverser(request)
        self.assertEqual(info['context'].__uri__, self.content_uri)
        self.assertEqual(info['view_name'], 'index.html')
        self.assertEqual(info['traversed'], ('folder','content'))

    def test_traverser_folder_subcontent_view2(self):
        self._create_content()

        request = self._makeRequest(
            {'PATH_INFO': '/test//folder//content/index.html'})

        root = self.factory(request)
        traverser = ITraverser(root)

        info = traverser(request)
        self.assertEqual(info['context'].__uri__, self.content_uri)
        self.assertEqual(info['view_name'], 'index.html')
        self.assertEqual(info['traversed'], ('folder','content'))
