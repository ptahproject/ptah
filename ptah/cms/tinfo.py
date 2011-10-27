""" type implementation """
import ptah, sys, logging
import sqlalchemy as sqla
from ptah import config
from zope import interface

from node import Session
from content import Content
from container import Container
from cms import buildClassActions
from events import ContentCreatedEvent
from interfaces import Forbidden, ContentSchema, ITypeInformation

log = logging.getLogger('ptah.cms')

TYPES_DIR_ID = 'ptah-cms:type'

@ptah.resolver('cms-type')
def typeInfoResolver(uri):
    """Type resolver"""
    return config.registry.storage[TYPES_DIR_ID].get(uri)


def get_type(tp):
    return config.registry.storage[TYPES_DIR_ID].get(tp)


def get_types():
    return config.registry.storage[TYPES_DIR_ID]


class TypeInformation(object):
    interface.implements(ITypeInformation)

    fieldset = None
    description = u''
    permission = ptah.NOT_ALLOWED

    addview = None # addview action, path relative to current container
    filter_content_types = False
    allowed_content_types = ()
    global_allow = True

    def __init__(self, cls, name, title, fieldset, **kw):
        self.__dict__.update(kw)

        self.__uri__ = 'cms-type:%s'%name

        self.cls = cls
        self.name = name
        self.title = title
        self.fieldset = fieldset

    def create(self, **data):
        content = self.cls(**data)
        config.notify(ContentCreatedEvent(content))
        return content

    def is_allowed(self, container):
        if not isinstance(container, Container):
            return False

        if self.permission:
            return ptah.check_permission(self.permission, container)
        return True

    def check_context(self, container):
        if not self.is_allowed(container):
            raise Forbidden()

    def list_types(self, container):
        if container.__type__ is not self or \
               not isinstance(container, Container):
            return ()

        types = []
        all_types = config.registry.storage[TYPES_DIR_ID]

        if self.filter_content_types:
            for tinfo in self.allowed_content_types:
                if isinstance(tinfo, basestring):
                    tinfo = all_types.get('cms-type:%s'%tinfo)

                if tinfo and tinfo.is_allowed(container):
                    types.append(tinfo)
        else:
            for tinfo in all_types.values():
                if tinfo.global_allow and tinfo.is_allowed(container):
                    types.append(tinfo)

        return types


# we have to generate seperate sql query for each type
_sql_get = ptah.QueryFreezer(
    lambda: Session.query(Content)
    .filter(Content.__uri__ == sqla.sql.bindparam('uri')))


def Type(name, title=None, fieldset=None, **kw):
    """ Declare new type. This function has to be called within a content
    class declaration.

    .. code-block:: python

        class MyContent(ptah.cms.Content):

            __type__ = Type('My content')

    """
    info = config.DirectiveInfo(allowed_scope=('class',))

    fs = ContentSchema if fieldset is None else fieldset

    if title is None:
        title = name.capitalize()

    typeinfo = TypeInformation(None, name, title, fs, **kw)

    f_locals = sys._getframe(1).f_locals
    if '__mapper_args__' not in f_locals:
        f_locals['__mapper_args__'] = {'polymorphic_identity': typeinfo.__uri__}
    if '__id__' not in f_locals and '__tablename__' in f_locals:
        f_locals['__id__'] = sqla.Column(
            'id', sqla.Integer,
            sqla.ForeignKey('ptah_cms_content.id'), primary_key=True)
    if '__uri_factory__' not in f_locals:
        f_locals['__uri_factory__'] = ptah.UriFactory('cms-%s'%name)

        def resolve_content(uri):
            return _sql_get.first(uri=uri)

        resolve_content.__doc__ = 'CMS Content resolver for %s type'%title

        ptah.register_uri_resolver('cms-%s'%name, resolve_content, depth = 2)

    info.attach(
        config.ClassAction(
            registerType, (typeinfo, name, fieldset), kw,
            discriminator = (TYPES_DIR_ID, name))
        )

    return typeinfo


excludeNames = ('expires', 'contributors', 'creators', 'view', 'subjects',
                'publisher', 'effective', 'created', 'modified')
def namesFilter(name, fieldNames=None):
    if fieldNames is not None and name in fieldNames:
        return True

    if name in excludeNames:
        return False

    return not name.startswith('_')


def registerType(
    config, cls, tinfo, name, fieldset,
    permission = ptah.NOT_ALLOWED, fieldNames=None, **kw):

    # generate schema
    if fieldset is None:
        fieldset = ptah.generateFieldset(
            cls, fieldNames=fieldNames, namesFilter=namesFilter)
        log.info("Generating fieldset for %s content type.", cls)

    if 'global_allow' not in kw and not issubclass(cls, Content):
        kw['global_allow'] = False

    tinfo.__dict__.update(kw)

    if fieldset is not None:
        tinfo.fieldset = fieldset

    tinfo.cls = cls
    tinfo.permission = permission

    config.storage[TYPES_DIR_ID][tinfo.__uri__] = tinfo

    # build cms actions
    buildClassActions(cls)
