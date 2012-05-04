""" type implementation """
import sys, logging
import sqlalchemy as sqla
from zope.interface import implementer
from pyramid.compat import string_types
from pyramid.threadlocal import get_current_registry
from pyramid.exceptions import ConfigurationError

import ptah
from ptah import config
from ptah.uri import ID_RESOLVER
from ptah.security import NOT_ALLOWED
from ptah.interfaces import ITypeInformation, Forbidden, TypeException

log = logging.getLogger('ptah')

TYPES_DIR_ID = 'ptah:type'


@ptah.resolver('type')
def typeInfoResolver(uri):
    """Type resolver

       :Parameters:
         - type scheme, e.g. blob-sql
       :Returns:
         - :py:class:`ptah.TypeInformation`
    """
    return config.get_cfg_storage(TYPES_DIR_ID).get(uri)


def get_type(uri):
    """ Get registered type.

    :param uri: string identifier for TypeInformation, e.g. `type:sqlblob`

    :Returns:
      - :py:class:`ptah.TypeInformation`

    """
    return config.get_cfg_storage(TYPES_DIR_ID).get(uri)


def get_types():
    """ Get all registered types.

    :Returns:
      - mapping of all registered identifier and TypeInformation
    """
    return config.get_cfg_storage(TYPES_DIR_ID)


phase_data = []

class phase2(object):

    def __init__(self, name):
        self.name = name
        for n, _ in phase_data:
            if n == name:
                raise ConfigurationError(
                    'type phase "%s" is already registered'%name)

    def __call__(self, callback):
        phase_data.append((self.name, callback))
        return callback


@implementer(ITypeInformation)
class TypeInformation(object):
    """ Type information """

    title = ''
    description = ''

    fieldset = None
    permission = NOT_ALLOWED

    filter_content_types = False
    allowed_content_types = ()
    global_allow = False

    add_method = None

    def __init__(self, cls, name, **kw):
        self.__dict__.update(kw)

        self.__uri__ = 'type:%s'%name

        self.cls = cls
        self.name = name

    def add(self, content, *args, **kw):
        if self.add_method is None:
            raise TypeException("Add method is not defined")

        return self.add_method(content, *args, **kw)

    def create(self, **data):
        content = self.cls(**data)
        get_current_registry().notify(ptah.events.ContentCreatedEvent(content))
        return content

    def is_allowed(self, container):
        if self.permission:
            return ptah.check_permission(self.permission, container)
        return True

    def check_context(self, container):
        if not self.is_allowed(container):
            raise Forbidden()

    def list_types(self, container):
        if container.__type__ is not self:
            return ()

        types = []
        all_types = config.get_cfg_storage(TYPES_DIR_ID)

        if self.filter_content_types:
            allowed_types = self.allowed_content_types
            if callable(allowed_types):
                allowed_types = allowed_types(container)

            for tinfo in allowed_types:
                if isinstance(tinfo, string_types):
                    tinfo = all_types.get('type:%s'%tinfo)

                if tinfo and tinfo.is_allowed(container):
                    types.append(tinfo)
        else:
            for tinfo in all_types.values():
                if tinfo.global_allow and tinfo.is_allowed(container):
                    types.append(tinfo)

        return types


class type(object):
    """ Declare new type. This function has to be called within a content
    class declaration.

    .. code-block:: python

        @ptah.type('My content')
        class MyContent(object):
            pass

    """

    def __init__(self, name, title=None, **kw):
        self.name = name
        self.info = config.DirectiveInfo()
        kw['title'] = name.capitalize() if title is None else title
        self.kw = kw

    def __call__(self, cls):
        typeinfo = TypeInformation(cls, self.name, **self.kw)
        cls.__type__ = typeinfo

        # config actino and introspection info
        discr = (TYPES_DIR_ID, self.name)
        intr = config.Introspectable(
            TYPES_DIR_ID, discr, self.name, TYPES_DIR_ID)
        intr['name'] = self.name
        intr['type'] = typeinfo
        intr['codeinfo'] = self.info.codeinfo

        def register_type_impl(cfg):
            # run phase handlers
            for name, handler in phase_data:
                handler(cfg, cls, typeinfo, self.name, **self.kw)

            cfg.get_cfg_storage(TYPES_DIR_ID)[typeinfo.__uri__] = typeinfo

        self.info.attach(
            config.Action(register_type_impl,
                          discriminator=discr, introspectables=(intr,))
            )

        return cls


def sqla_add_method(content, *args, **kw):
    sa = ptah.get_session()
    sa.add(content)
    sa.flush()
    return content


@phase2('sqla')
def register_sqla_type(config, cls, tinfo, name, **kw):
    base = ptah.get_base()
    if not issubclass(cls, base):
        return

    # generate schema
    fieldset = tinfo.fieldset

    if fieldset is None:
        fieldset = ptah.generate_fieldset(
            cls, fieldNames=kw.get('fieldNames'),
            namesFilter=kw.get('namesFilter'))
        log.info("Generating fieldset for %s content type.", cls)

    if fieldset is not None:
        tinfo.fieldset = fieldset

    if tinfo.add_method is None:
        tinfo.add_method = sqla_add_method

    # install __uri__ property
    if not hasattr(cls, '__uri__'):
        pname = None
        for cl in cls.__table__.columns:
            if cl.primary_key:
                pname = cl.name
                break

        l = len(tinfo.name)+1
        cls.__uri__ = UriProperty(tinfo.name, cl.name)

        cls.__uri_sql_get__ = ptah.QueryFreezer(
            lambda: ptah.get_session().query(cls) \
                .filter(getattr(cls, pname) == sqla.sql.bindparam('uri')))

        def resolver(uri):
            """Content resolver for %s type'"""%tinfo.name
            return cls.__uri_sql_get__.first(uri=uri[l:])

        storage = config.get_cfg_storage(ID_RESOLVER)
        if tinfo.name in storage:
            raise ConfigurationError(
                'Resolver for "%s" already registered'%tinfo.name)
        storage[tinfo.name] = resolver


class UriProperty(object):

    def __init__(self, prefix, cname):
        self.cname = cname
        self.prefix = prefix

    def __get__(self, inst, cls):
        if inst is None:
            return self

        return '%s:%s'%(self.prefix, getattr(inst, self.cname))
