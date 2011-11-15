""" blob storage implementation """
import os
import sqlalchemy as sqla
from zope import interface

import ptah
from node import Node, Session
from interfaces import IBlob, IBlobStorage


class Blob(Node):
    interface.implements(IBlob)

    __tablename__ = 'ptah_blobs'
    __uri_factory__ = ptah.UriFactory('blob-sql')

    __id__ = sqla.Column('id', sqla.Integer,
                         sqla.ForeignKey('ptah_nodes.id'), primary_key=True)

    mimetype = sqla.Column(sqla.String(), default='')
    filename = sqla.Column(sqla.String(), default='')
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


class BlobStorage(object):
    interface.implements(IBlobStorage)

    _sql_get = ptah.QueryFreezer(
        lambda: Session.query(Blob)
            .filter(Blob.__uri__ == sqla.sql.bindparam('uri')))

    _sql_get_by_parent = ptah.QueryFreezer(
        lambda: Session.query(Blob)
            .filter(Blob.__parent_uri__ == sqla.sql.bindparam('parent')))

    def create(self, parent=None):
        blob = Blob(__parent__=parent)
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


blobStorage = BlobStorage()

ptah.register_uri_resolver('blob-sql', blobStorage.get)
