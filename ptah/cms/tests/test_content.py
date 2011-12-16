import time
import transaction
from datetime import datetime

import ptah
from ptah import config
from ptah.testing import PtahTestCase


class TestContent(PtahTestCase):

    def _make_app(self):
        global ApplicationRoot
        class ApplicationRoot(ptah.cms.ApplicationRoot):
            __type__ = ptah.cms.Type('app')

        ApplicationRoot.__type__.cls = ApplicationRoot

        return ApplicationRoot

    def test_content_path(self):
        import ptah.cms

        class MyContent(ptah.cms.Content):

            __mapper_args__ = {'polymorphic_identity': 'mycontent'}
            __uri_factory__ = ptah.UriFactory('mycontent')

        ApplicationRoot = self._make_app()

        factory = ptah.cms.ApplicationFactory(
            ApplicationRoot, '/app1', 'root', 'Root App')

        root = factory(self.request)

        content = MyContent(__name__='test',
                            __parent__ = root,
                            __path__ = '%stest/'%root.__path__)
        c_uri = content.__uri__
        ptah.get_session().add(content)

        self.assertTrue(
            content.__name__ == 'test')

        self.assertTrue(
            content.__resource_url__(self.request, {}) == '/app1/test/')
        transaction.commit()

        # same content inside same root but in different app factory

        factory2 = ptah.cms.ApplicationFactory(
            ApplicationRoot, '/app2', 'root', 'Root App')
        root = factory2(self.request)

        c = ptah.get_session().query(MyContent).filter(
            MyContent.__uri__ == c_uri).one()

        self.assertTrue(
            c.__resource_url__(self.request, {}) == '/app2/test/')

    def test_content_events(self):
        import ptah.cms

        class MyContent(ptah.cms.Content):
            __mapper_args__ = {'polymorphic_identity': 'mycontent'}
            __uri_factory__ = ptah.UriFactory('mycontent')

        content = MyContent()

        self.registry.notify(ptah.events.ContentCreatedEvent(content))

        self.assertTrue(isinstance(content.created, datetime))
        self.assertTrue(isinstance(content.modified, datetime))
        time.sleep(0.1)

        self.registry.notify(ptah.events.ContentModifiedEvent(content))
        self.assertTrue(content.modified != content.created)

    def test_content_set_owner_on_create(self):
        import ptah, ptah.cms

        class MyContent(ptah.cms.Content):
            __mapper_args__ = {'polymorphic_identity': 'mycontent'}
            __uri_factory__ = ptah.UriFactory('mycontent')

        content = MyContent()

        self.registry.notify(ptah.events.ContentCreatedEvent(content))

        self.assertEqual(content.__owner__, None)

        ptah.auth_service.set_userid('user')
        self.registry.notify(ptah.events.ContentCreatedEvent(content))

        self.assertEqual(content.__owner__, 'user')

    def test_content_info(self):
        import ptah, ptah.cms

        class MyContent(ptah.cms.Content):
            __mapper_args__ = {'polymorphic_identity': 'mycontent'}
            __uri_factory__ = ptah.UriFactory('mycontent')

        content = MyContent()
        self.registry.notify(ptah.events.ContentCreatedEvent(content))

        info = content.info()
        self.assertIn('__name__', info)
        self.assertIn('__type__', info)

        class MyContent(ptah.cms.Content):
            __type__ = ptah.cms.Type('mycontent', 'MyContent')

        content = MyContent()
        self.registry.notify(ptah.events.ContentCreatedEvent(content))

        info = content.info()
        self.assertIn('title', info)
        self.assertIn('description', info)

    def test_content_update(self):
        import ptah, ptah.cms

        class MyContent(ptah.cms.Content):
            __type__ = ptah.cms.Type('mycontent', 'MyContent')

        content = MyContent()
        self.registry.notify(ptah.events.ContentCreatedEvent(content))

        modified = content.modified
        time.sleep(0.1)

        content.update(title='Test title')
        info = content.info()

        self.assertEqual(info['title'], 'Test title')
        self.assertEqual(content.title, 'Test title')
        self.assertTrue(content.modified > modified)

    def test_content_delete(self):
        import ptah, ptah.cms

        class MyContent(ptah.cms.Content):
            __type__ = ptah.cms.Type('mycontent', 'MyContent')

        class MyContainer(ptah.cms.Container):
            __type__ = ptah.cms.Type('container', 'Container')

        content = MyContent()

        self.assertRaises(ptah.cms.Error, content.delete)

        container = MyContainer()
        container['content'] = content

        content.delete()
        self.assertEqual(container.keys(), [])
