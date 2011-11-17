""" uri resolver """
import uuid
from ptah import config

RESOLVER_ID = 'ptah:uri-resolver'


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
        return config.get_cfg_storage(RESOLVER_ID)[schema](uri)
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
        info.attach(
            config.Action(
                _register_uri_resolver, (schema, func),
                discriminator=(RESOLVER_ID, schema))
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
    info = config.DirectiveInfo(depth=depth)
    info.attach(
        config.Action(
            _register_uri_resolver, (schema, resolver),
            discriminator=(RESOLVER_ID, schema))
        )


def _register_uri_resolver(cfg, schema, resolver):
    cfg.get_cfg_storage(RESOLVER_ID)[schema] = resolver


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
        return '%s:%s' % (self.schema, uuid.uuid4().get_hex())
