import transaction
from io import BytesIO
from pyramid.compat import bytes_, binary_type, text_type
from ptah.testing import PtahTestCase


class TestBlob(PtahTestCase):

    def test_blob(self):
        import ptah.cms

        blob = ptah.cms.blob_storage.add(BytesIO(bytes_('blob data','utf-8')))
        self.assertTrue(ptah.cms.IBlob.providedBy(blob))
        self.assertEqual(blob.read(), bytes_('blob data','utf-8'))
        self.assertTrue(ptah.cms.IBlobStorage.providedBy(ptah.cms.blob_storage))

    def test_blob_create(self):
        import ptah.cms

        blob = ptah.cms.blob_storage.create()
        self.assertTrue(ptah.cms.IBlob.providedBy(blob))
        self.assertEqual(blob.read(), None)

    def test_blob_metadata(self):
        import ptah.cms

        blob = ptah.cms.blob_storage.add(
            BytesIO(bytes_('blob data','utf-8')),
            filename='test.txt', mimetype='text/plain')

        self.assertEqual(blob.filename, 'test.txt')
        self.assertEqual(blob.mimetype, 'text/plain')

    def test_blob_info(self):
        import ptah.cms
        blob = ptah.cms.blob_storage.add(
            BytesIO(bytes_('blob data','utf-8')),
            filename='test.txt', mimetype='text/plain')

        info = blob.info()
        self.assertEqual(info['__uri__'], blob.__uri__)
        self.assertEqual(info['filename'], 'test.txt')
        self.assertEqual(info['mimetype'], 'text/plain')

    def test_blob_resolver(self):
        import ptah

        blob = ptah.cms.blob_storage.add(BytesIO(bytes_('blob data','utf-8')))

        blob_uri = blob.__uri__
        transaction.commit()

        blob = ptah.resolve(blob_uri)

        self.assertEqual(blob.__uri__, blob_uri)
        self.assertEqual(blob.read(), bytes_('blob data','utf-8'))

    def test_blob_with_parent(self):
        import ptah

        class MyContent(ptah.cms.Node):
            __name__ = ''
            __mapper_args__ = {'polymorphic_identity': 'mycontent'}
            __uri_factory__ = ptah.UriFactory('test')

        content = MyContent()
        content_uri = content.__uri__
        ptah.get_session().add(content)

        blob_uri = ptah.cms.blob_storage.add(
            BytesIO(bytes_('blob data','utf-8')), content).__uri__
        transaction.commit()

        blob = ptah.resolve(blob_uri)
        self.assertEqual(blob.__parent_ref__.__uri__, content_uri)

        blob = ptah.cms.blob_storage.getByParent(content_uri)
        self.assertEqual(blob.__uri__, blob_uri)

    def test_blob_write(self):
        import ptah

        blob_uri = ptah.cms.blob_storage.add(
            BytesIO(bytes_('blob data','utf-8'))).__uri__
        blob = ptah.resolve(blob_uri)
        blob.write(bytes_('new data','utf-8'))
        transaction.commit()

        blob = ptah.resolve(blob_uri)
        self.assertEqual(blob.read(), bytes_('new data','utf-8'))

    def test_blob_rest_data(self):
        import ptah.cms
        from ptah.cms.rest import blobData

        blob = ptah.cms.blob_storage.add(
            BytesIO(bytes_('blob data','utf-8')),
            filename='test.txt', mimetype='text/plain')

        response = blobData(blob, self.request)
        self.assertEqual(response.body, bytes_('blob data','utf-8'))
        self.assertEqual(
            response.headerlist,
            [('Content-Type', bytes_('text/plain')),
             ('Content-Disposition', bytes_('filename="test.txt"','utf-8')),
             ('Content-Length', '9')])

    def test_blob_rest_data_headers_unicode(self):
        import ptah.cms
        from ptah.cms.rest import blobData

        blob = ptah.cms.blob_storage.add(
            BytesIO(bytes_('blob data','utf-8')),
            filename='test.jpg', mimetype=text_type('image/jpeg'))

        response = blobData(blob, self.request)

        headers = response.headers
        for hdr in headers:
            if hdr.lower() != 'content-length':
                self.assertTrue(isinstance(headers[hdr], binary_type))
