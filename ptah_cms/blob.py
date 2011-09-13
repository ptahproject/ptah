""" blob storage implementation """
import os
import sqlalchemy as sqla
from zope import interface

import ptah

from node import Node, Session
from interfaces import IBlob, IBlobStorage


class Blob(Node):
    interface.implements(IBlob)

    __tablename__ = 'ptah_blobstorage'
    __mapper_args__ = {'polymorphic_identity': 'ptah-blob'}

    __id__ = sqla.Column(
        'id', sqla.Integer, sqla.ForeignKey('ptah_nodes.id'), primary_key=True)

    mimetype = sqla.Column(sqla.Unicode, default=u'')
    filename = sqla.Column(sqla.Unicode, default=u'')
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


class Storage(object):

    def blobRef(self, uuid):
        return 'blob://%s:%s'%(self.name, uuid)


class BlobStorage(Storage):
    interface.implements(IBlobStorage)

    name = 'sql'

    _sql_get = ptah.QueryFreezer(
        lambda: Session.query(Blob)
            .filter(Blob.__uuid__ == sqla.sql.bindparam('uuid')))

    _sql_get_by_parent = ptah.QueryFreezer(
        lambda: Session.query(Blob)
            .filter(Blob.__parent_id__ == sqla.sql.bindparam('parent')))

    def add(self, data, parent=None, **metadata):
        data.seek(0)
        
        blob = Blob(__parent__=parent)
        blob.data = data.read()
        blob.updateMetadata(**metadata)

        data.seek(0, os.SEEK_END)
        blob.size = data.tell()
        Session.add(blob)
        Session.flush()

        return self.blobRef(blob.__uuid__)

    def get(self, uuid):
        return self._sql_get.first(uuid=uuid)

    def getByParent(self, parent):
        return self._sql_get_by_parent.first(parent=parent)

    def replace(self, uuid, data, **metadata):
        pass

    def remove(self, uuid):
        pass


blobStorage = BlobStorage()

ptah.registerResolver(
    'blob', 'sql', blobStorage.get,
    title='SQL Blob storage resolver')
