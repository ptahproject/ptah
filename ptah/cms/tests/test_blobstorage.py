import transaction
from cStringIO import StringIO

from base import Base


class TestBlob(Base):

    def test_blob(self):
        import ptah.cms

        blob = ptah.cms.blobStorage.add(StringIO('blob data'))
        self.assertTrue(ptah.cms.IBlob.providedBy(blob))
        self.assertEqual(blob.read(), 'blob data')
        self.assertTrue(ptah.cms.IBlobStorage.providedBy(ptah.cms.blobStorage))

    def test_blob_create(self):
        import ptah.cms

        blob = ptah.cms.blobStorage.create()
        self.assertTrue(ptah.cms.IBlob.providedBy(blob))
        self.assertEqual(blob.read(), None)

    def test_blob_metadata(self):
        import ptah.cms

        blob = ptah.cms.blobStorage.add(
            StringIO('blob data'), filename='test.txt', mimetype='text/plain')

        self.assertEqual(blob.filename, 'test.txt')
        self.assertEqual(blob.mimetype, 'text/plain')

    def test_blob_info(self):
        import ptah.cms
        blob = ptah.cms.blobStorage.add(
            StringIO('blob data'), filename='test.txt', mimetype='text/plain')

        info = blob.info()
        self.assertEqual(info['__uri__'], blob.__uri__)
        self.assertEqual(info['filename'], 'test.txt')
        self.assertEqual(info['mimetype'], 'text/plain')

    def test_blob_resolver(self):
        import ptah

        blob = ptah.cms.blobStorage.add(StringIO('blob data'))

        blob_uri = blob.__uri__

        blob = ptah.resolve(blob_uri)

        self.assertEqual(blob.__uri__, blob_uri)
        self.assertEqual(blob.read(), 'blob data')

    def test_blob_with_parent(self):
        import ptah

        class MyContent(ptah.cms.Node):
            __name__ = ''
            __mapper_args__ = {'polymorphic_identity': 'mycontent'}
            __uri_factory__ = ptah.UriFactory('test')

        content = MyContent()
        content_uri = content.__uri__
        ptah.cms.Session.add(content)

        blob_uri = ptah.cms.blobStorage.add(
            StringIO('blob data'), content).__uri__
        transaction.commit()

        blob = ptah.resolve(blob_uri)
        self.assertEqual(blob.__parent_ref__.__uri__, content_uri)

        blob = ptah.cms.blobStorage.getByParent(content_uri)
        self.assertEqual(blob.__uri__, blob_uri)

    def test_blob_write(self):
        import ptah

        blob_uri = ptah.cms.blobStorage.add(StringIO('blob data')).__uri__
        blob = ptah.resolve(blob_uri)
        blob.write('new data')
        transaction.commit()

        blob = ptah.resolve(blob_uri)
        self.assertEqual(blob.read(), 'new data')

    def test_blob_rest_data(self):
        import ptah.cms
        from ptah.cms.rest import blobData
        from pyramid.testing import DummyRequest

        blob = ptah.cms.blobStorage.add(
            StringIO('blob data'), filename='test.txt', mimetype='text/plain')

        request = DummyRequest()

        response = blobData(blob, request)
        self.assertEqual(response.body, 'blob data')
        self.assertEqual(
            response.headerlist,
            [('Content-Disposition', 'filename="test.txt"'),
             ('Content-Length', '9')])
