""" type implementation """
import ptah
import sys, colander
import sqlalchemy as sqla
from memphis import config
from zope import interface
from pyramid.httpexceptions import HTTPForbidden
from pyramid.threadlocal import get_current_request

from node import Session
from content import Session, Content
from container import Container
from events import ContentCreatedEvent
from interfaces import ContentSchema, ITypeInformation
from permissions import View, AddContent, ModifyContent


Types = {}


class TypeInformation(object):
    interface.implements(ITypeInformation)

    add = None # add action, path relative to current container
    description = u''
    permission = AddContent

    filter_content_types = False
    allowed_content_types = ()
    global_allow = True

    def __init__(self, klass, name, title,
                 schema=ContentSchema(), constructor=None, **kw):
        self.__dict__.update(kw)

        self.name = name
        self.title = title
        self.klass = klass
        self.schema = schema

        if constructor is None:
            constructor = self._constructor
        self.constructor = constructor

    def _constructor(self, **data):
        attrs = {}

        if self.schema is not None:
            for node in self.schema:
                val = data.get(node.name, node.default)
                if val is not colander.null:
                    attrs[node.name] = val

        return self.klass(**attrs)

    def create(self, **data):
        content = self.constructor(**data)
        Session.add(content)

        request = get_current_request()
        if request is not None:
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
            raise HTTPForbidden()

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
    .filter(Content.__uuid__ == sqla.sql.bindparam('uuid')))

def resolveContent(uuid):
    return _sql_get.first(uuid=uuid)


def Type(name, title, **kw):
    info = config.DirectiveInfo(allowed_scope=('class',))

    typeinfo = TypeInformation(None, name, title)

    f_locals = sys._getframe(1).f_locals
    if '__mapper_args__' not in f_locals:
        f_locals['__mapper_args__'] = {'polymorphic_identity': name}
    if '__id__' not in f_locals and '__tablename__' in f_locals:
        f_locals['__id__'] = sqla.Column( #pragma: no cover
            'id', sqla.Integer,
            sqla.ForeignKey('ptah_cms_content.id'), primary_key=True)
    if '__uuid_generator__' not in f_locals:
        f_locals['__uuid_generator__'] = ptah.UUIDGenerator('cms+%s'%name)

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
    klass, tinfo, name,
    title = '',
    description = '',
    schema = ContentSchema(),
    permission = ptah.NOT_ALLOWED, **kw):

    tinfo.__dict__.update(kw)

    if isinstance(schema, colander._SchemaMeta):
        schema = schema()

    tinfo.klass = klass
    tinfo.schema = schema
    tinfo.description = description
    tinfo.permission = permission

    Types[name] = tinfo


class IAction(interface.Interface):
    """ marker interface for actions """


class Action(object):
    interface.implements(IAction)

    id = ''
    title = ''
    description = ''
    action = ''
    actionFactory = None
    condition = None
    permission = None
    sortWeight = 1.0,
    data = None

    def __init__(self, id='', **kw):
        self.id = id
        self.__dict__.update(kw)

    def url(self, context, request, url=''):
        if self.actionFactory is not None:
            return self.actionFactory(context, request)

        if self.action.startswith('/'):
            return '%s%s'%(request.application_url, self.action)
        else:
            return '%s%s'%(url, self.action)

    def check(self, context, request):
        if self.permission:
            if not ptah.checkPermission(
                self.permission, context, request, False):
                return False

        if self.condition is not None:
            return self.condition(context, request)

        return True


def _contentAction(id, context, ac):
    config.registry.registerAdapter(ac, (context,), IAction, id)


def contentAction(context, id, title,
                  description = '',
                  action='', condition=None, permission=None,
                  sortWeight = 1.0, **kw):

    kwargs = {'id': id,
              'title': title,
              'description': description,
              'condition': condition,
              'permission': permission,
              'sortWeight': sortWeight,
              'data': kw}

    if callable(action):
        kwargs['actionFactory'] = action
    else:
        kwargs['action'] = action

    ac = Action(**kwargs)
    info = config.DirectiveInfo()

    info.attach(
        config.Action(
            _contentAction, (id, context, ac,),
            discriminator = ('ptah-cms:action', id, context))
        )


def listActions(content, request):
    url = request.resource_url(content)

    actions = []
    for name, action in config.registry.adapters.lookupAll(
        (interface.providedBy(content),), IAction):
        if action.check(content, request):
            actions.append(
                (action.sortWeight,
                 {'id': action.id,
                  'url': action.url(content, request, url),
                  'title': action.title,
                  'description': action.description,
                  'data': action.data}))

    actions.sort()
    return [ac for _w, ac in actions]


@config.addCleanup
def cleanUp():
    Types.clear()
