import uuid
import transaction
from memphis import config
from datetime import datetime

from base import Base


class TestContent(Base):

    def test_content_path(self):
        import ptah_cms
        self._setRequest(self._makeRequest())

        class MyContent(ptah_cms.Content):

            __mapper_args__ = {'polymorphic_identity': 'mycontent'}

            def __uuid_generator__(self):
                return uuid.uuid4().get_hex()


        factory = ptah_cms.ApplicationFactory('/app1', 'root', 'Root App')

        root = factory(self.request)

        content = MyContent(__name__='test',
                            __parent__ = root,
                            __path__ = '%stest/'%root.__path__)
        c_uuid = content.__uuid__
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
            MyContent.__uuid__ == c_uuid).one()

        self.assertTrue(
            c.__resource_url__(self.request, {}) == '/app2/test/')

    def test_content_events(self):
        import ptah_cms

        class MyContent(ptah_cms.Content):
            __mapper_args__ = {'polymorphic_identity': 'mycontent'}
            def __uuid_generator__(self):
                return uuid.uuid4().get_hex()

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
            def __uuid_generator__(self):
                return uuid.uuid4().get_hex()

        content = MyContent()

        config.notify(ptah_cms.ContentCreatedEvent(content))

        self.assertEqual(content.__owner__, None)

        ptah.authService.setUserId('user')
        config.notify(ptah_cms.ContentCreatedEvent(content))

        self.assertEqual(content.__owner__, 'user')
