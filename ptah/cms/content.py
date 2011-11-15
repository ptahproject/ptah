""" Base content class """
import sqlalchemy as sqla
from sqlalchemy.ext.hybrid import hybrid_property

from zope import interface
from ptah import config, form

import ptah
from ptah.cms import events
from ptah.cms.node import Node, Session
from ptah.cms.interfaces import Error, IContent
from ptah.cms.security import action
from ptah.cms.permissions import DeleteContent, ModifyContent


class Content(Node):
    """ Base class for content objects. A content class should inherit from
    `Content` to participate in content hierarchy traversal.

    .. attribute:: __path__

       A string used by the :py:class:`ptah.cms.ContentTraverser` which is
       used for efficient resolution of URL structure to content models.
       This is internal implementation and manually editing it can break
       your hierarchy.

    .. attribute:: __name__

       This is the identifier in a container if you are using containment and
       hierarchies.

    .. attribute:: title

       Content title which is editable by end user.

    .. attribute:: description

       Content description which is editable by end user.

    .. attribute:: view

       A URI which can be resolved with :py:func:`ptah.resolve` function
       which represents the 'default' view for content. Akin to index.html
       or default.php in Apache.

    .. attribute:: created

       Content creation time which is set by
       :py:func:`ptah.cms.events.createdHandler` during object creation.

       :type: :py:class:`datetime.datetime`

    .. attribute:: modified

       Content modification time which is set by
       :py:func:`ptah.cms.events.modifiedHandler` during object modification.

       :type: :py:class:`datetime.datetime`

    .. attribute:: effective

       :type: :py:class:`datetime.datetime` or None

    .. attribute:: expires

       :type: :py:class:`datetime.datetime` or None

    .. attribute:: creators

       a :py:class:`ptah.JsonListType` which contains sequence of users.  Using
       principal URIs is a good idea.

    .. attribute:: subjects

       a :py:class:`ptah.JsonListType` which contains sequence of subjects.
       Holding a sequence of URIs could resolve to subject objects. Or you can
       use strings.

    .. attribute: publisher

       a Unicode string which should identify the publisher.

    .. attribute: contributors

       a :py:class:`ptah.JsonListType` which contains sequence of contributors.
       You could keep a sequence of principal URIs.
    """

    interface.implements(IContent)

    __tablename__ = 'ptah_content'

    __id__ = sqla.Column('id', sqla.Integer,
                         sqla.ForeignKey('ptah_nodes.id'), primary_key=True)
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
                val = data.get(field.name, field.default)
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
