""" Base content class """
import sqlalchemy as sqla
from sqlalchemy.ext.hybrid import hybrid_property

from zope import interface
from memphis import config, form
from collections import OrderedDict

import ptah
from ptah_cms import events
from ptah_cms.cms import action
from ptah_cms.node import Node, Session, load_parents
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
    description = sqla.Column(sqla.Unicode, default=u'',
                              info = {'missing': u'', 'field_type': 'textarea'})
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

    def __init__(self, **kw):
        super(Content, self).__init__(**kw)

        if self.__name__ and self.__parent__ is not None:
            self.__path__ = '%s%s/'%(self.__parent__.__path__, self.__name__)

    @hybrid_property
    def __name__(self):
        return self.__name_id__

    @__name__.setter
    def __name__(self, value):
        self.__name_id__ = value

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

            for field in tinfo.fieldset.fields():
                val = data.get(field.name,  field.default)
                if val is not form.null:
                    setattr(self, field.name, val)

            config.notify(events.ContentModifiedEvent(self))

    def _extra_info(self, info):
        if self.__type__:
            fieldset = self.__type__.fieldset.bind()
            for field in fieldset.fields():
                val = getattr(self, field.name, field.default)
                info[field.name] = field.serialize(val)

        info['view'] = self.view
        info['created'] = self.created
        info['modified'] = self.modified
        info['effective'] = self.effective
        info['expires'] = self.expires

    def info(self):
        info = super(Content, self).info()
        info['__name__'] = self.__name__
        info['__content__'] = True
        info['__container__'] = False
        self._extra_info(info)
        return info
