""" Base container class implementation """
import sqlalchemy as sqla
from zope import interface
from memphis import config

import ptah
from ptah_cms import events
from ptah_cms.node import Node, Session
from ptah_cms.content import Content, loadParents
from ptah_cms.interfaces import IContainer


class Container(Content):
    interface.implements(IContainer)

    def keys(self):
        return [c.__name__ for c in self.__children__]

    def get(self, key, default=None):
        item = self._sql_get_in_parent.first(key=key, parent=self.__uuid__)
        if item is not None:
            item.__parent__ = self
        return item

    def __contains__(self, key):
        return key in self.keys()

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

        if item.__uuid__ == self.__uuid__:
            raise ValueError("Can't set to it self")

        parents = [p.__uuid__ for p in loadParents(self)]
        if item.__uuid__ in parents:
            raise TypeError("Can't itself to chidlren")

        if key in self.keys():
            raise KeyError(key)

        if item.__parent_id__ is None:
            event = events.ContentAddedEvent(item)
        else:
            event = events.ContentMovedEvent(item)

        item.__name__ = key
        item.__parent__ = self
        item.__parent_id__ = self.__uuid__
        item.__path__ = '%s%s/'%(self.__path__, key)

        # recursevly update children paths
        def update_path(container):
            path = container.__path__
            for item in container.__children__:
                item.__path__ = '%s%s/'%(path, item.__name__)

                if isinstance(item, Container):
                    update_path(item)

        if isinstance(item, Container):
            update_path(item)

        config.notify(event)

    def __delitem__(self, item):
        if isinstance(item, basestring):
            item = self[item]

        if item.__parent__ is self:
            if isinstance(item, Container):
                for key in item.keys():
                    del item[key]

            config.notify(events.ContentDeletingEvent(item))

            Session.delete(item)
            return

        raise KeyError(item)
