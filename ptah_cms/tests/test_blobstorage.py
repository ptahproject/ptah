import ptah
import transaction
from cStringIO import StringIO
from memphis import config

from base import Base


class TestBlob(Base):

    def test_blob(self):
        import ptah_cms

        blob = ptah_cms.blobStorage.add(StringIO('blob data'))
        self.assertTrue(ptah_cms.IBlob.providedBy(blob))
        self.assertEqual(blob.read(), 'blob data')
        self.assertTrue(ptah_cms.IBlobStorage.providedBy(ptah_cms.blobStorage))

    def test_blob_create(self):
        import ptah_cms

        blob = ptah_cms.blobStorage.create()
        self.assertTrue(ptah_cms.IBlob.providedBy(blob))
        self.assertEqual(blob.read(), None)

    def test_blob_metadata(self):
        import ptah_cms

        blob = ptah_cms.blobStorage.add(
            StringIO('blob data'), filename='test.txt', mimetype='text/plain')

        self.assertEqual(blob.filename, 'test.txt')
        self.assertEqual(blob.mimetype, 'text/plain')

    def test_blob_info(self):
        import ptah_cms
        blob = ptah_cms.blobStorage.add(
            StringIO('blob data'), filename='test.txt', mimetype='text/plain')

        info = blob.info()
        self.assertEqual(info['__uri__'], blob.__uri__)
        self.assertEqual(info['filename'], 'test.txt')
        self.assertEqual(info['mimetype'], 'text/plain')

    def test_blob_resolver(self):
        import ptah, ptah_cms

        blob = ptah_cms.blobStorage.add(StringIO('blob data'))

        blob_uri = blob.__uri__

        blob = ptah.resolve(blob_uri)

        self.assertEqual(blob.__uri__, blob_uri)
        self.assertEqual(blob.read(), 'blob data')

    def test_blob_with_parent(self):
        import ptah, ptah_cms

        class MyContent(ptah_cms.Node):
            __mapper_args__ = {'polymorphic_identity': 'mycontent'}
            __uri_generator__ = ptah.UriGenerator('test')

        content = MyContent()
        content_uri = content.__uri__
        ptah_cms.Session.add(content)

        blob_uri = ptah_cms.blobStorage.add(
            StringIO('blob data'), content).__uri__
        transaction.commit()

        blob = ptah.resolve(blob_uri)
        self.assertEqual(blob.__parent_ref__.__uri__, content_uri)

        blob = ptah_cms.blobStorage.getByParent(content_uri)
        self.assertEqual(blob.__uri__, blob_uri)

    def test_blob_write(self):
        import ptah, ptah_cms

        blob_uri = ptah_cms.blobStorage.add(StringIO('blob data')).__uri__
        blob = ptah.resolve(blob_uri)
        blob.write('new data')
        transaction.commit()

        blob = ptah.resolve(blob_uri)
        self.assertEqual(blob.read(), 'new data')
