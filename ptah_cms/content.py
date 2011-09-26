""" Base content class """
import sqlalchemy as sqla
from zope import interface

import ptah
from ptah_cms.node import Node, Session
from ptah_cms.interfaces import IContent


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
        .filter(Content.__uuid__ == sqla.sql.bindparam('uuid')))

    _sql_get_in_parent = ptah.QueryFreezer(
        lambda: Session.query(Content)
            .filter(Content.__name_id__ == sqla.sql.bindparam('key'))
            .filter(Content.__parent_id__ == sqla.sql.bindparam('parent')))

    _sql_parent = ptah.QueryFreezer(
        lambda: Session.query(Content)
            .filter(Content.__uuid__ == sqla.sql.bindparam('parent')))

    def __get_name(self):
        return self.__name_id__

    def __set_name(self, value):
        self.__name_id__ = value

    __name__ = property(__get_name, __set_name)

    def __resource_url__(self, request, info):
        return '%s%s'%(request.root.__root_path__,
                       self.__path__[len(request.root.__path__):])
