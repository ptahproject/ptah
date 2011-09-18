""" Base container class implementation """
import sqlalchemy as sqla
from zope import interface
from zope.component import getSiteManager
from pyramid.httpexceptions import HTTPForbidden

import ptah
from ptah.security import checkPermission

import events
from node import Node, Session
from content import Content
from interfaces import IContainer


class Container(Content):
    interface.implements(IContainer)

    def keys(self):
        return [c.name for c in self.__children__]

    def get(self, key, default=None):
        item = self._sql_get_in_parent.first(key=key, parent=self.__uuid__)
        if item is not None:
            item.__parent__ = self
        return item

    def __getitem__(self, key):
        try:
            item = self._sql_get_in_parent.one(key=key, parent=self.__uuid__)
            item.__parent__ = self
            return item
        except sqla.orm.exc.NoResultFound:
            raise KeyError(key)

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
        item.__path__ = '%s%s/'%(self.__path__, key)

        # recursevly update children paths
        def update_path(container):
            path = container.__path__
            for item in container.__children__:
                item.__path__ = '%s%s/'%(path, item.name)

                if isinstance(item, Container):
                    update_path(item)

        if isinstance(item, Container):
            update_path(item)

        getSiteManager().notify(event)

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


def loadContent(uuid, permission=None):
    item = ptah.resolve(uuid)

    parents = []

    parent = item
    while parent is not None:
        if not isinstance(parent, Node):
            break

        if parent.__parent__ is None:
            parent.__parent__ = parent.__parent_ref__
        parent = parent.__parent__

    if permission is not None:
        if not checkPermission(item, permission):
            return HTTPForbidden

    return item


def loadParents(content):
    pass
