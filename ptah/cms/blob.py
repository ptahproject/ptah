""" blob storage implementation """
import os
import sqlalchemy as sqla
from pyramid.compat import text_type
from zope.interface import implementer

import ptah
from ptah.cms.node import Node
from ptah.cms.interfaces import IBlob, IBlobStorage


@implementer(IBlob)
class Blob(Node):
    """ simple blob implementation """

    __tablename__ = 'ptah_blobs'
    __mapper_args__ = {'polymorphic_identity': 'blob-sql'}
    __uri_factory__ = ptah.UriFactory('blob-sql')

    __id__ = sqla.Column('id', sqla.Integer,
                         sqla.ForeignKey('ptah_nodes.id'), primary_key=True)

    mimetype = sqla.Column(sqla.String(128), default=text_type(''))
    filename = sqla.Column(sqla.String(255), default=text_type(''))
    size = sqla.Column(sqla.Integer, default=0)
    data = sqla.orm.deferred(sqla.Column(sqla.LargeBinary))

    def read(self):
        return self.data

    def write(self, data):
        self.data = data
        self.size = len(data)

    def updateMetadata(self, mimetype=None, filename=None, **md):
        if mimetype is not None:
            self.mimetype = mimetype

        if filename is not None:
            self.filename = filename

    def info(self):
        info = super(Blob, self).info()

        info['size'] = self.size
        info['mimetype'] = self.mimetype
        info['filename'] = self.filename
        return info


@implementer(IBlobStorage)
class BlobStorage(object):
    """ simple blob storage """

    _sql_get = ptah.QueryFreezer(
        lambda: ptah.get_session().query(Blob)
            .filter(Blob.__uri__ == sqla.sql.bindparam('uri')))

    _sql_get_by_parent = ptah.QueryFreezer(
        lambda: ptah.get_session().query(Blob)
            .filter(Blob.__parent_uri__ == sqla.sql.bindparam('parent')))

    def create(self, parent=None):
        blob = Blob(__parent__=parent)
        Session = ptah.get_session()
        Session.add(blob)
        Session.flush()

        return blob

    def add(self, data, parent=None, **metadata):
        blob = self.create(parent)

        data.seek(0)

        blob.data = data.read()
        blob.updateMetadata(**metadata)

        data.seek(0, os.SEEK_END)
        blob.size = data.tell()

        return blob

    def get(self, uri):
        """SQL Blob resolver"""
        return self._sql_get.first(uri=uri)

    def getByParent(self, parent):
        return self._sql_get_by_parent.first(parent=parent)

    def replace(self, uri, data, **metadata): # pragma: no cover
        pass

    def remove(self, uri): # pragma: no cover
        pass


blob_storage = BlobStorage()

ptah.resolver.register('blob-sql', blob_storage.get)
