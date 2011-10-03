import ptah
import transaction
from memphis import config
from datetime import datetime

from base import Base


class TestContent(Base):

    def tearDown(self):
        config.cleanUp(self.__class__.__module__)
        super(TestContent, self).tearDown()

    def test_content_path(self):
        import ptah_cms
        self._setRequest(self._makeRequest())

        class MyContent(ptah_cms.Content):

            __mapper_args__ = {'polymorphic_identity': 'mycontent'}
            __uri_generator__ = ptah.UriGenerator('mycontent')


        factory = ptah_cms.ApplicationFactory('/app1', 'root', 'Root App')

        root = factory(self.request)

        content = MyContent(__name__='test',
                            __parent__ = root,
                            __path__ = '%stest/'%root.__path__)
        c_uri = content.__uri__
        ptah_cms.Session.add(content)

        self.assertTrue(
            content.__name__ == 'test')

        self.assertTrue(
            content.__resource_url__(self.request, {}) == '/app1/test/')
        transaction.commit()

        # same content inside same root but in different app factory

        factory2 = ptah_cms.ApplicationFactory('/app2', 'root', 'Root App')
        root = factory2(self.request)

        c = ptah_cms.Session.query(MyContent).filter(
            MyContent.__uri__ == c_uri).one()

        self.assertTrue(
            c.__resource_url__(self.request, {}) == '/app2/test/')

    def test_content_events(self):
        import ptah_cms

        class MyContent(ptah_cms.Content):
            __mapper_args__ = {'polymorphic_identity': 'mycontent'}
            __uri_generator__ = ptah.UriGenerator('mycontent')

        content = MyContent()

        config.notify(ptah_cms.ContentCreatedEvent(content))

        self.assertTrue(isinstance(content.created, datetime))
        self.assertTrue(isinstance(content.modified, datetime))

        config.notify(ptah_cms.ContentModifiedEvent(content))
        self.assertTrue(content.modified != content.created)

    def test_content_set_owner_on_create(self):
        import ptah, ptah_cms

        class MyContent(ptah_cms.Content):
            __mapper_args__ = {'polymorphic_identity': 'mycontent'}
            __uri_generator__ = ptah.UriGenerator('mycontent')

        content = MyContent()

        config.notify(ptah_cms.ContentCreatedEvent(content))

        self.assertEqual(content.__owner__, None)

        ptah.authService.setUserId('user')
        config.notify(ptah_cms.ContentCreatedEvent(content))

        self.assertEqual(content.__owner__, 'user')

    def test_content_info(self):
        import ptah, ptah_cms

        class MyContent(ptah_cms.Content):
            __mapper_args__ = {'polymorphic_identity': 'mycontent'}
            __uri_generator__ = ptah.UriGenerator('mycontent')

        content = MyContent()
        config.notify(ptah_cms.ContentCreatedEvent(content))

        info = content.info()
        self.assertIn('__name__', info)
        self.assertIn('__type__', info)

        class MyContent(ptah_cms.Content):
            __type__ = ptah_cms.Type('mycontent', 'MyContent')

        content = MyContent()
        config.notify(ptah_cms.ContentCreatedEvent(content))

        info = content.info()
        self.assertIn('title', info)
        self.assertIn('description', info)

    def test_content_update(self):
        import ptah, ptah_cms

        class MyContent(ptah_cms.Content):
            __type__ = ptah_cms.Type('mycontent', 'MyContent')

        content = MyContent()
        config.notify(ptah_cms.ContentCreatedEvent(content))

        modified = content.modified

        content.update(title='Test title')
        info = content.info()

        self.assertEqual(info['title'], 'Test title')
        self.assertEqual(content.title, 'Test title')
        self.assertTrue(content.modified > modified)

    def test_content_delete(self):
        import ptah, ptah_cms

        class MyContent(ptah_cms.Content):
            __type__ = ptah_cms.Type('mycontent', 'MyContent')

        class MyContainer(ptah_cms.Container):
            __type__ = ptah_cms.Type('container', 'Container')

        content = MyContent()

        self.assertRaises(ptah_cms.Error, content.delete)

        container = MyContainer()
        container['content'] = content

        content.delete()
        self.assertEqual(container.keys(), [])
