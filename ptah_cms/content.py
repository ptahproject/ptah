""" Base content class """
import colander
import sqlalchemy as sqla
from zope import interface
from memphis import config
from collections import OrderedDict

import ptah
from ptah_cms import events
from ptah_cms.cms import action
from ptah_cms.node import Node, Session, loadParents
from ptah_cms.interfaces import Error
from ptah_cms.interfaces import IContent
from ptah_cms.permissions import View, DeleteContent, ModifyContent


class Content(Node):
    """ Base class for content objects. Class has to inherit from `Content` 
    to participat in content hiararchy.

    .. attribute:: __path__

    .. attribute:: __name__

    .. attribute:: title

       Content title

    .. attribute:: description

       Content description

    .. attribute:: created

       Content creation time

       :type: :py:class:`datetime.datetime`

    .. attribute:: modified

       Content modification time

       :type: :py:class:`datetime.datetime`

    .. attribute:: effective

       :type: :py:class:`datetime.datetime` or None

    .. attribute:: expires

       :type: :py:class:`datetime.datetime` or None

    """

    interface.implements(IContent)

    __tablename__ = 'ptah_cms_content'

    __id__ = sqla.Column('id', sqla.Integer,
                         sqla.ForeignKey('ptah_cms_nodes.id'), primary_key=True)
    __path__ = sqla.Column('path', sqla.Unicode, default=u'')
    __name_id__ = sqla.Column('name', sqla.Unicode(255))

    title = sqla.Column(sqla.Unicode, default=u'')
    description = sqla.Column(sqla.Unicode, default=u'')
    view = sqla.Column(sqla.Unicode, default=u'')

    created = sqla.Column(sqla.DateTime)
    modified = sqla.Column(sqla.DateTime)
    effective = sqla.Column(sqla.DateTime)
    expires = sqla.Column(sqla.DateTime)

    creators = sqla.Column(ptah.JsonListType(), default=[])
    subjects = sqla.Column(ptah.JsonListType(), default=[])
    publisher = sqla.Column(sqla.Unicode, default=u'')
    contributors = sqla.Column(ptah.JsonListType(), default=[])

    # sql queries
    _sql_get = ptah.QueryFreezer(
        lambda: Session.query(Content)
        .filter(Content.__uri__ == sqla.sql.bindparam('uri')))

    _sql_get_in_parent = ptah.QueryFreezer(
        lambda: Session.query(Content)
            .filter(Content.__name_id__ == sqla.sql.bindparam('key'))
            .filter(Content.__parent_uri__ == sqla.sql.bindparam('parent')))

    _sql_parent = ptah.QueryFreezer(
        lambda: Session.query(Content)
            .filter(Content.__uri__ == sqla.sql.bindparam('parent')))

    def __get_name(self):
        return self.__name_id__

    def __set_name(self, value):
        self.__name_id__ = value

    __name__ = property(__get_name, __set_name)

    def __resource_url__(self, request, info):
        return '%s%s'%(request.root.__root_path__,
                       self.__path__[len(request.root.__path__):])

    @action(permission=DeleteContent)
    def delete(self):
        parent = self.__parent__
        if parent is None:
            parent = self.__parent_ref__

        if parent is None:
            raise Error("Can't find parent")

        del parent[self]

    @action(permission=ModifyContent)
    def update(self, **data):
        if self.__type__:
            tinfo = self.__type__

            for node in tinfo.schema:
                val = data.get(node.name, node.default)
                if val is not colander.null:
                    setattr(self, node.name, val)

            config.notify(events.ContentModifiedEvent(self))

    def _extra_info(self, info):
        if self.__type__:
            for node in self.__type__.schema:
                val = getattr(self, node.name, node.missing)
                try:
                    info[node.name] = node.serialize(val)
                except:
                    info[node.name] = node.default

        info['view'] = self.view
        info['created'] = self.created
        info['modified'] = self.modified
        info['effective'] = self.effective
        info['expires'] = self.expires

    @action(permission=View)
    def info(self):
        info = OrderedDict(
            (('__name__', self.__name__),
             ('__type__', self.__type_id__),
             ('__uri__', self.__uri__),
             ('__container__', False),
             ('__parents__', [p.__uri__ for p in 
                              loadParents(self) if isinstance(p, Node)]),
             ))

        self._extra_info(info)
        return info
