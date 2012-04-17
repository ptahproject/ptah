""" type implementation """
import sys, logging
import sqlalchemy as sqla

import ptah
from ptah import config
from ptah.cms.content import Content
from ptah.cms.container import BaseContainer
from ptah.cms.security import build_class_actions
from ptah.cms.interfaces import ContentSchema

from ptah.tinfo import TYPES_DIR_ID, TypeInformation

log = logging.getLogger('ptah.cms')


@ptah.resolver('cms-type')
def typeInfoResolver(uri):
    """Type resolver

       :Parameters:
         - type scheme, e.g. blob-sql
       :Returns:
         - :py:class:`ptah.cms.TypeInformation`
    """
    return config.get_cfg_storage(TYPES_DIR_ID).get(uri[4:])


class TypeInformation(TypeInformation):
    """ Type information """

    schema = None
    global_allow = True
    addview = None # addview action, path relative to current container

    def __init__(self, cls, name, **kw):
        super(TypeInformation, self).__init__(cls, name, **kw)

        self.__uri__ = 'cms-type:%s'%name

    def is_allowed(self, container):
        if not isinstance(container, BaseContainer):
            return False

        return super(TypeInformation, self).is_allowed(container)

    def list_types(self, container):
        if not isinstance(container, BaseContainer):
            return ()

        return super(TypeInformation, self).list_types(container)


def Type(name, title=None, fieldset=None, **kw):
    """ Declare new type. This function has to be called within a content
    class declaration.

    .. code-block:: python

        class MyContent(ptah.cms.Content):

            __type__ = Type('My content')

    """
    info = config.DirectiveInfo(allowed_scope=('class',))

    kw['title'] = name.capitalize() if title is None else title
    fs = ContentSchema if fieldset is None else fieldset

    typeinfo = TypeInformation(None, name, fieldset=fs, **kw)

    f_locals = sys._getframe(1).f_locals
    if '__mapper_args__' not in f_locals:
        f_locals['__mapper_args__'] = {'polymorphic_identity': typeinfo.__uri__}

    if '__id__' not in f_locals and '__tablename__' in f_locals:
        f_locals['__id__'] = sqla.Column(
            'id', sqla.Integer,
            sqla.ForeignKey('ptah_content.id'), primary_key=True)
    if '__uri_factory__' not in f_locals:
        schema = 'cms-{0}'.format(name)
        typeinfo.schema = schema

        f_locals['__uri_factory__'] = ptah.UriFactory(schema)

        def resolve_content(uri):
            return typeinfo.cls.__uri_sql_get__.first(uri=uri)

        resolve_content.__doc__ = 'CMS Content resolver for %s type'%name

        ptah.resolver(schema, 2)(resolve_content)

    # config actino and introspection info
    discr = (TYPES_DIR_ID, name)
    intr = config.Introspectable(TYPES_DIR_ID, discr, name, TYPES_DIR_ID)
    intr['name'] = name
    intr['type'] = typeinfo
    intr['codeinfo'] = info.codeinfo

    info.attach(
        config.ClassAction(
            register_type_impl, (typeinfo, name, fieldset), kw,
            discriminator=discr, introspectables=(intr,))
        )
    return typeinfo


excludeNames = ('expires', 'contributors', 'creators', 'view', 'subjects',
                'publisher', 'effective', 'created', 'modified')
def names_filter(name, fieldNames=None):
    if fieldNames is not None and name in fieldNames:
        return True

    if name in excludeNames:
        return False

    return not name.startswith('_')


def register_type_impl(
    config, cls, tinfo, name, fieldset=None, fieldNames=None, **kw):

    # generate schema
    fieldset = kw.get('fieldset')
    if fieldset is None:
        kw['fieldset'] = ptah.generate_fieldset(
            cls, fieldNames=fieldNames, namesFilter=names_filter)
        log.info("Generating fieldset for %s content type.", cls)

    if 'global_allow' not in kw and not issubclass(cls, Content):
        kw['global_allow'] = False

    tinfo.__dict__.update(kw)

    tinfo.cls = cls

    config.get_cfg_storage(TYPES_DIR_ID)[tinfo.__uri__[4:]] = tinfo

    # sql query for content resolver
    cls.__uri_sql_get__ = ptah.QueryFreezer(
        lambda: ptah.get_session().query(cls) \
            .filter(cls.__uri__ == sqla.sql.bindparam('uri')))

    # build cms actions
    build_class_actions(cls)
