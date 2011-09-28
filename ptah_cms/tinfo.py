""" type implementation """
import ptah
import sys, colander
import sqlalchemy as sqla
from memphis import config
from zope import interface

from node import Session
from content import Session, Content
from container import Container
from events import ContentCreatedEvent
from interfaces import Forbidden
from interfaces import ContentSchema, ITypeInformation
from permissions import AddContent


Types = {}


@ptah.resolver('type', 'Type resolver')
def typeInfoResolver(uri):
    return Types.get(uri[5:])


class TypeInformation(object):
    interface.implements(ITypeInformation)

    add = None # add action, path relative to current container
    description = u''
    permission = AddContent

    filter_content_types = False
    allowed_content_types = ()
    global_allow = True

    def __init__(self, factory, name, title, schema=None, **kw):
        self.__dict__.update(kw)

        self.__uri__ = 'type:%s'%name

        self.factory = factory
        self.name = name
        self.title = title
        self.schema = schema

    def create(self, **data):
        content = self.factory(**data)
        config.notify(ContentCreatedEvent(content))
        return content

    def isAllowed(self, container):
        if not isinstance(container, Container):
            return False

        if self.permission:
            return ptah.checkPermission(
                self.permission, container, throw=False)
        return True

    def checkContext(self, container):
        if not self.isAllowed(container):
            raise Forbidden()

    def listTypes(self, container):
        if container.__type__ is not self or \
               not isinstance(container, Container):
            return ()

        types = []
        if self.filter_content_types:
            for tname in self.allowed_content_types:
                tinfo = Types.get(tname)
                if tinfo and tinfo.isAllowed(container):
                    types.append(tinfo)

        else:
            for tinfo in Types.values():
                if tinfo.global_allow and tinfo.isAllowed(container):
                    types.append(tinfo)

        return types


# we have to generate seperate sql query for each type
_sql_get = ptah.QueryFreezer(
    lambda: Session.query(Content)
    .filter(Content.__uri__ == sqla.sql.bindparam('uri')))

def resolveContent(uri):
    return _sql_get.first(uri=uri)


_contentSchema = ContentSchema()

def Type(name, title, schema = None, **kw):
    info = config.DirectiveInfo(allowed_scope=('class',))

    if schema is None:
        schema = _contentSchema

    if isinstance(schema, colander._SchemaMeta):
        schema = schema()

    typeinfo = TypeInformation(None, name, title, schema)

    f_locals = sys._getframe(1).f_locals
    if '__mapper_args__' not in f_locals:
        f_locals['__mapper_args__'] = {'polymorphic_identity': name}
    if '__id__' not in f_locals and '__tablename__' in f_locals:
        f_locals['__id__'] = sqla.Column( #pragma: no cover
            'id', sqla.Integer,
            sqla.ForeignKey('ptah_cms_content.id'), primary_key=True)
    if '__uri_generator__' not in f_locals:
        f_locals['__uri_generator__'] = ptah.UriGenerator('cms+%s'%name)

        ptah.registerResolver(
            'cms+%s'%name, resolveContent,
            title = 'Ptah CMS Content resolver for %s type'%title,
            depth = 2)

    info.attach(
        config.ClassAction(
            registerType,
            (typeinfo, name, title), kw,
            discriminator = ('ptah-cms:type', name))
        )

    return typeinfo


def registerType(
    factory, tinfo, name,
    title = '',
    description = '',
    permission = ptah.NOT_ALLOWED, **kw):

    tinfo.__dict__.update(kw)

    tinfo.factory = factory
    tinfo.description = description
    tinfo.permission = permission

    Types[name] = tinfo


@config.addCleanup
def cleanUp():
    Types.clear()
