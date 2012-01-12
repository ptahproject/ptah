""" Base content class """
import sqlalchemy as sqla
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime
from zope.interface import implementer
from pyramid.compat import text_type
from pyramid.threadlocal import get_current_registry

import ptah
from ptah.cms.node import Node
from ptah.cms.interfaces import Error, IContent
from ptah.cms.security import action
from ptah.cms.permissions import DeleteContent, ModifyContent


class BaseContent(Node):
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

    .. attribute:: created

       Content creation time which is set by
       :py:func:`ptah.cms.content.createdHandler` during object creation.

       :type: :py:class:`datetime.datetime`

    .. attribute:: modified

       Content modification time which is set by
       :py:func:`ptah.cms.content.modifiedHandler` during object modification.

       :type: :py:class:`datetime.datetime`

    .. attribute:: effective

       :type: :py:class:`datetime.datetime` or None

    .. attribute:: expires

       :type: :py:class:`datetime.datetime` or None

    .. attribute:: lang

       Content language code. `en` is default value.

    """

    __tablename__ = 'ptah_content'

    __id__ = sqla.Column('id', sqla.Integer,
                         sqla.ForeignKey('ptah_nodes.id'), primary_key=True)
    __path__ = sqla.Column('path', sqla.Unicode(1024),
                           default=text_type(''), index=True)
    __name_id__ = sqla.Column('name', sqla.Unicode(255), default=text_type(''))

    title = sqla.Column(sqla.Unicode(1024), default=text_type(''))
    description = sqla.Column(sqla.UnicodeText, default=text_type(''),
                              info = {'missing': '', 'field_type': 'textarea'})

    created = sqla.Column(sqla.DateTime)
    modified = sqla.Column(sqla.DateTime)
    effective = sqla.Column(sqla.DateTime)
    expires = sqla.Column(sqla.DateTime)
    lang = sqla.Column(sqla.String(12), default='en', info={'skip':True})

    # sql queries
    _sql_get = ptah.QueryFreezer(
        lambda: ptah.get_session().query(BaseContent)
        .filter(BaseContent.__uri__ == sqla.sql.bindparam('uri')))

    _sql_get_in_parent = ptah.QueryFreezer(
        lambda: ptah.get_session().query(BaseContent)
            .filter(BaseContent.__name_id__ == sqla.sql.bindparam('key'))
            .filter(BaseContent.__parent_uri__ == sqla.sql.bindparam('parent')))

    _sql_parent = ptah.QueryFreezer(
        lambda: ptah.get_session().query(BaseContent)
            .filter(BaseContent.__uri__ == sqla.sql.bindparam('parent')))

    def __init__(self, **kw):
        super(BaseContent, self).__init__(**kw)

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
                if val is not ptah.form.null:
                    setattr(self, field.name, val)

            get_current_registry().notify(
                ptah.events.ContentModifiedEvent(self))

    def _extra_info(self, info):
        if self.__type__:
            fieldset = self.__type__.fieldset.bind()
            for field in fieldset.fields():
                val = getattr(self, field.name, field.default)
                info[field.name] = field.serialize(val)

        info['created'] = self.created
        info['modified'] = self.modified
        info['effective'] = self.effective
        info['expires'] = self.expires

    def info(self):
        info = super(BaseContent, self).info()
        info['__name__'] = self.__name__
        info['__content__'] = True
        info['__container__'] = False
        self._extra_info(info)
        return info


@implementer(IContent)
class Content(BaseContent):
    """ Content """


@ptah.subscriber(ptah.events.ContentCreatedEvent)
def content_created_handler(ev):
    """ Assigns created, modified, __owner__
        attributes for newly created content """
    now = datetime.utcnow()
    ev.object.created = now
    ev.object.modified = now

    user = ptah.auth_service.get_userid()
    if user:
        ev.object.__owner__ = user


@ptah.subscriber(ptah.events.ContentModifiedEvent)
def content_modified_handler(ev):
    """ Updates the modified attribute on content """
    ev.object.modified = datetime.utcnow()


@ptah.subscriber(ptah.events.ContentEvent)
def content_event_handler(ev):
    """ Resend uri invalidate event """
    get_current_registry().notify(
        ptah.events.UriInvalidateEvent(ev.object.__uri__))
