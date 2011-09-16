""" type implementation """
import ptah
import sys, colander
import sqlalchemy as sqla
from memphis import config
from zope import interface

from content import Session, Content
from permissions import View, ModifyContent
from interfaces import ContentSchema, IAction, ITypeInformation


registered = {}

class Action(object):
    interface.implements(IAction)

    id = ''
    title = ''
    description = ''
    action = ''
    permission = None

    def __init__(self, id='', **kw):
        self.id = id
        self.__dict__.update(kw)


class TypeInformation(object):
    interface.implements(ITypeInformation)

    add = None # add action, path relative to current container
    description = u''

    def __init__(self, factory, name, title, schema=None, **kw):
        self.__dict__.update(kw)

        self.name = name
        self.title = title
        self.factory = factory
        self.schema = schema

    def __reduce__(self):
        return getType, (self.id,)

    def create(self, **data):
        instance = Instance(aq_base(self))

        # load datasheets
        for schId in self.schemas:
            if schId in data:
                if isinstance(data[schId], Datasheet):
                    ds = instance.getDatasheet(schId)
                    ds.__load__(data[schId])

        event.notify(ObjectCreatedEvent(instance))
        return instance


# we have to generate seperate sql query for each type
sql_get = ptah.QueryFreezer(
    lambda: Session.query(Content)
    .filter(Content.__uuid__ == sqla.sql.bindparam('uuid')))


def resolveContent(uuid):
    return sql_get.first(uuid=uuid)


def Type(name, title, **kw):
    info = config.DirectiveInfo(allowed_scope=('class',))

    typeinfo = TypeInformation(None, name, title)

    f_locals = sys._getframe(1).f_locals
    if '__mapper_args__' not in f_locals:
        f_locals['__mapper_args__'] = {'polymorphic_identity': name}
    if '__id__' not in f_locals and '__tablename__' in f_locals:
        f_locals['__id__'] = sqla.Column(
            'id', sqla.Integer, 
            sqla.ForeignKey('ptah_cms_content.id'), primary_key=True)
    if '__uuid_generator__' not in f_locals:
        f_locals['__uuid_generator__'] = ptah.UUIDGenerator('cms+%s'%name)

        ptah.registerResolver(
            'cms+%s'%name, resolveContent, 
            title='Ptah CMS Content resolver for %s type'%title)

    info.attach(
        config.ClassAction(
            registerType,
            (typeinfo, name, title), kw,
            discriminator = ('ptah-cms:type', name))
        )

    return typeinfo


def registerType(
    klass, tinfo, name,
    title = '', description = '', schema = ContentSchema,
    global_allow = True, permission = View,
    actions = None, **kw):

    if actions is None:
        actions = (
            Action(**{'id': 'view',
                      'title': 'View',
                      'action': '',
                      'permission': View}),
            Action(**{'id': 'edit',
                      'title': 'Edit',
                      'action': 'edit.html',
                      'permission': ModifyContent}),
            )

    tinfo.__dict__.update(kw)

    if isinstance(schema, colander._SchemaMeta):
        schema = schema()

    tinfo.schema = schema
    tinfo.factory = klass
    tinfo.description = description
    tinfo.global_allow = global_allow
    tinfo.permission = permission
    tinfo.actions = actions

    registered[name] = tinfo


@config.addCleanup
def cleanUp():
    registered.clear()
