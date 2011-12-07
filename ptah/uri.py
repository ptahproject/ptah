""" uri resolver """
import uuid
import ptah
from ptah import config

ID_RESOLVER = 'ptah:resolver'


def resolve(uri):
    """ Resolve uri, return resolved object.

    Uri contains two parts, `schema` and `uuid`. `schema` is used for
    resolver selection. `uuid` is resolver specific data. By default
    uuid is a uuid.uuid4 string.
    """
    if not uri:
        return

    try:
        schema, data = uri.split(':', 1)
    except ValueError:
        return None

    try:
        return config.get_cfg_storage(ID_RESOLVER)[schema](uri)
    except KeyError:
        pass

    return None


def extract_uri_schema(uri):
    """ Extract schema of given uri """
    if uri:
        try:
            schema, data = uri.split(':', 1)
            return schema
        except:
            pass

    return None


def resolver(schema):
    """ Register resolver for given schema
    """
    info = config.DirectiveInfo()

    def wrapper(func):
        discr = (ID_RESOLVER, schema)

        intr = config.Introspectable(ID_RESOLVER,discr,func.__doc__,ID_RESOLVER)
        intr['schema'] = schema
        intr['callable'] = func

        info.attach(
            config.Action(
                _register_uri_resolver, (schema, func),
                discriminator=discr,
                introspectables = (intr,))
            )

        return func

    return wrapper


def register_uri_resolver(schema, resolver, depth=1):
    """ Register resolver for given schema

    :param schema: uri schema
    :type schema: string
    :param resolver: Callable object that accept one parameter.

    Resolver interface::

      class Resolver(object):

         def __call__(self, uri):
             return content
    """
    discr = (ID_RESOLVER, schema)
    info = config.DirectiveInfo(depth=depth)

    intr = config.Introspectable(ID_RESOLVER,discr,resolver.__doc__,ID_RESOLVER)
    intr['schema'] = schema
    intr['callable'] = resolver

    info.attach(
        config.Action(
            _register_uri_resolver, (schema, resolver),
            discriminator=discr, introspectables = (intr,))
        )


def _register_uri_resolver(cfg, schema, resolver):
    cfg.get_cfg_storage(ID_RESOLVER)[schema] = resolver


def pyramid_uri_resolver(config, schema, resolver):
    """ pyramid configurator directive 'ptah_uri_resolver' """
    discr = (ID_RESOLVER, schema)
    intr = ptah.config.Introspectable(
        ID_RESOLVER,discr,resolver.__doc__,ID_RESOLVER)
    intr['schema'] = schema
    intr['callable'] = resolver

    config.action(
        discr,
        lambda config, schema, resolver:
            config.get_cfg_storage(ID_RESOLVER).update({schema:resolver}),
        (config, schema, resolver), introspectables = (intr,))


class UriFactory(object):
    """ Uri Generator

    Example::

       >> uri = UriFactory('cms-content')

       >> uri()
       'cms-content:f73f3266fa15438e94cca3621a3f2dbc'

    """

    def __init__(self, schema):
        self.schema = schema

    def __call__(self):
        """ Generate new uri using supplied schema """
        return '%s:%s' % (self.schema, uuid.uuid4().hex)
