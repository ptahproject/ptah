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
from sqlschema import generateSchema


Types = {}

@ptah.resolver('cms+type', 'Type resolver')
def typeInfoResolver(uri):
    return Types.get(uri[9:])


class TypeInformation(object):
    interface.implements(ITypeInformation)

    add = None # add action, path relative to current container
    description = u''
    permission = AddContent

    schema = None
    schemaNodes = None

    filter_content_types = False
    allowed_content_types = ()
    global_allow = True

    def __init__(self, factory, name, title, schema=ContentSchema(), **kw):
        self.__dict__.update(kw)

        self.__uri__ = 'cms+type:%s'%name

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
            for tinfo in self.allowed_content_types:
                if isinstance(tinfo, basestring):
                    tinfo = Types.get(tinfo)

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


def Type(name, title, schema = None, **kw):
    info = config.DirectiveInfo(allowed_scope=('class',))

    if isinstance(schema, colander._SchemaMeta):
        schema = schema()

    kwargs = {}
    if schema is not None:
        kwargs['schema'] = schema

    typeinfo = TypeInformation(None, name, title, **kwargs)

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
            (typeinfo, name, schema), kw,
            discriminator = ('ptah-cms:type', name))
        )

    return typeinfo


def registerType(
    factory, tinfo, name, schema,
    permission = ptah.NOT_ALLOWED, schemaNodes=None, **kw):

    if schema is None:
        # generate schema
        schema = generateSchema(factory, schemaNodes=schemaNodes)

    tinfo.__dict__.update(kw)

    if schema:
        tinfo.schema = schema

    tinfo.factory = factory
    tinfo.permission = permission

    Types[name] = tinfo


@config.addCleanup
def cleanUp():
    Types.clear()
