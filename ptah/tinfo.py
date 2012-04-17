""" type implementation """
import sys, logging
import sqlalchemy as sqla
from zope.interface import implementer
from pyramid.compat import string_types
from pyramid.threadlocal import get_current_registry
from pyramid.exceptions import ConfigurationError

import ptah
from ptah import config
from ptah.interfaces import ITypeInformation, Forbidden, TypeException
from ptah.security import NOT_ALLOWED

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


phase2_data = []


class phase2(object):

    def __init__(self, name):
        self.name = name
        for n, _ in phase2_data:
            if n == name:
                raise ConfigurationError(
                    'type phase2 "%s" is already registered'%name)

    def __call__(self, callback):
        phase2_data.append((self.name, callback))
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

    def add(self, container, content):
        if self.add_method is None:
            raise TypeException("Add method is not defined")

        return self.add_method(container, content)

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


def Type(name, **kw):
    """ Declare new type. This function has to be called within a content
    class declaration.

    .. code-block:: python

        class MyContent(object):

            __type__ = Type('My content')

    """
    info = config.DirectiveInfo(allowed_scope=('class',))

    if kw.get('title') is None:
        kw['title'] = name.capitalize()

    typeinfo = TypeInformation(None, name, **kw)

    # config actino and introspection info
    discr = (TYPES_DIR_ID, name)
    intr = config.Introspectable(TYPES_DIR_ID, discr, name, TYPES_DIR_ID)
    intr['name'] = name
    intr['type'] = typeinfo
    intr['codeinfo'] = info.codeinfo

    info.attach(
        config.ClassAction(
            register_type_impl, (typeinfo, name), kw,
            discriminator=discr, introspectables=(intr,))
        )
    return typeinfo


def register_type_impl(config, cls, tinfo, name, **kw):
    tinfo.__dict__.update(kw)
    tinfo.cls = cls

    config.get_cfg_storage(TYPES_DIR_ID)[tinfo.__uri__] = tinfo

    # run phase2 handlers
    for name, handler in phase2_data:
        handler(config, cls, tinfo, name, **kw)


def sqla_add_method(container, content):
    ptah.get_session().add(content)
    return content


@phase2('sqla')
def register_sqla_type(config, cls, tinfo, name, **kw):
    base = ptah.get_base()
    if not issubclass(cls, base):
        return

    # generate schema
    fieldset = tinfo.fieldset

    if fieldset is None:
        fieldset = ptah.generate_fieldset(cls)
        log.info("Generating fieldset for %s content type.", cls)

    if fieldset is not None:
        tinfo.fieldset = fieldset

    if tinfo.add_method is None:
        tinfo.add_method = sqla_add_method
