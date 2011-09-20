import uuid
import transaction
from cStringIO import StringIO
from memphis import config

from base import Base


class TestBlob(Base):

    def test_blob(self):
        import ptah_cms

        self.assertTrue(ptah_cms.IBlobStorage.providedBy(ptah_cms.blobStorage))

        blob_uuid = ptah_cms.blobStorage.add(StringIO('blob data'))
        blob = ptah_cms.blobStorage.get(blob_uuid)
        
        self.assertTrue(ptah_cms.IBlob.providedBy(blob))
        self.assertEqual(blob.read(), 'blob data')

    def test_blob_metadata(self):
        import ptah_cms

        blob_uuid = ptah_cms.blobStorage.add(
            StringIO('blob data'), filename='test.txt', mimetype='text/plain')
        blob = ptah_cms.blobStorage.get(blob_uuid)
        
        self.assertEqual(blob.filename, 'test.txt')
        self.assertEqual(blob.mimetype, 'text/plain')

    def test_blob_resolver(self):
        import ptah, ptah_cms

        blob_uuid = ptah_cms.blobStorage.add(StringIO('blob data'))

        blob = ptah.resolve(blob_uuid)
        
        self.assertEqual(blob.__uuid__, blob_uuid)
        self.assertEqual(blob.read(), 'blob data')

    def test_blob_with_parent(self):
        import ptah, ptah_cms

        class MyContent(ptah_cms.Node):
            __mapper_args__ = {'polymorphic_identity': 'mycontent'}
            def __uuid_generator__(self):
                return uuid.uuid4().get_hex()

        content = MyContent()
        content_uuid = content.__uuid__
        ptah_cms.Session.add(content)
        
        blob_uuid = ptah_cms.blobStorage.add(
            StringIO('blob data'), content)
        transaction.commit()

        blob = ptah.resolve(blob_uuid)
        self.assertEqual(blob.__parent_ref__.__uuid__, content_uuid)

        blob = ptah_cms.blobStorage.getByParent(content_uuid)
        self.assertEqual(blob.__uuid__, blob_uuid)

    def test_blob_write(self):
        import ptah, ptah_cms

        blob_uuid = ptah_cms.blobStorage.add(StringIO('blob data'))
        blob = ptah.resolve(blob_uuid)
        blob.write('new data')
        transaction.commit()

        blob = ptah.resolve(blob_uuid)
        self.assertEqual(blob.read(), 'new data')
