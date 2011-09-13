""" Base content class implementation """
import sqlalchemy as sqla
from zope import interface
from pyramid.decorator import reify

import ptah
from ptah.utils import JsonType

from node import Node
from interfaces import IContent


class Content(Node):
    interface.implements(IContent)

    __tablename__ = 'ptah_contents'
    __id__ = sqla.Column('id', sqla.Integer, 
                         sqla.ForeignKey('ptah_nodes.id'), primary_key=True)
    name = sqla.Column(sqla.Unicode(255))

    title = sqla.Column(sqla.Unicode, default=u'')
    description = sqla.Column(sqla.Unicode, default=u'')

    created = sqla.Column(sqla.DateTime)
    modified = sqla.Column(sqla.DateTime)
    effective = sqla.Column(sqla.DateTime)
    expires = sqla.Column(sqla.DateTime)

    creators = sqla.Column(JsonType, default=[])
    subjects = sqla.Column(JsonType, default=[])
    publisher = sqla.Column(sqla.Unicode, default=u'')
    contributors = sqla.Column(JsonType, default=[])

    @reify
    def __name__(self):
        return self.name

    def __resource_url__(self, request, info):
        return '%s%s/'%(self.__parent__.__path__, self.name)
