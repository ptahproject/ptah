""" Base container class implementation """
import ptah
import sqlalchemy as sqla
from zope import interface
from zope.component import getSiteManager

import events
from node import Node, Session
from content import Content
from interfaces import IContainer


class Container(Content):
    interface.implements(IContainer)

    __tablename__ = 'ptah_containers'

    __id__ = sqla.Column(
        'id', sqla.Integer,
        sqla.ForeignKey('ptah_contents.id'), primary_key=True)
    __path__ = sqla.Column('path', sqla.Unicode, default=u'')

    # sql queries
    _sql_parent = ptah.QueryFreezer(
        lambda: Session.query(Container)
            .filter(Container.__uuid__ == sqla.sql.bindparam('parent')))

    _sql_get = ptah.QueryFreezer(
        lambda: Session.query(Content)
            .filter(Content.name == sqla.sql.bindparam('key'))
            .filter(Content.__parent_id__ == sqla.sql.bindparam('parent')))

    def __init__(self, *args, **kw):
        super(Container, self).__init__(*args, **kw)

        if self.__path__ is None:
            self._rebuildPath()

    def _rebuildPath(self):
        parent = self.__parent__
        if parent is None:
            parent = self._sql_parent.first(parent=self.__parent_id__)

        if parent is not None:
            self.__path__ = '%s%s/'%(parent.__path__, self.name)

    def get(self, key, default=None):
        item = self._sql_get.first(key=key, parent=self.__uuid__)
        if item is not None:
            item.__parent__ = self
        return item

    def keys(self):
        return [c.name for c in self.__children__]

    def __setitem__(self, key, item):
        if not isinstance(item, Content):
            raise ValueError("Content object is required")
        
        if key in self.keys():
            raise KeyError(key)

        if item.__parent_id__ and item.__parent_id__ != self.__uuid__:
            event = events.ContentMovedEvent(item)
        else:
            event = events.ContentAddedEvent(item)

        item.name = key
        item.__parent_id__ = self.__uuid__
        
        getSiteManager().notify(event)

    def __getitem__(self, key):
        try:
            item = self._sql_get.one(key=key, parent=self.__uuid__)
            item.__parent__ = self
            return item
        except sqla.orm.exc.NoResultFound:
            raise KeyError(key)

    def __delitem__(self, item):
        if isinstance(item, basestring):
            item = self[item]

        if item.__parent__ is self:
            if isinstance(item, Container):
                for key in item.keys():
                    del item[key]

            getSiteManager().notify(
                events.ContentDeletingEvent(item))

            Session.delete(item)
            return

        raise KeyError(item)

    def __resource_url__(self, request, info):
        return self.__path__


def loadContent(uuid):
    item = ptah.resolve(uuid)

    parents = []

    parent = item
    while parent is not None:
        if not isinstance(parent, Node):
            break

        if parent.__parent__ is None:
            parent.__parent__ = parent.__parent_ref__
        parent = parent.__parent__

    return item
