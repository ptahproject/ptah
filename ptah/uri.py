""" uri resolver """
import uuid
from memphis import config

resolvers = {}
resolversTitle = {}


def resolve(uri):
    """ Resolve uri, return resolved object.

    Uri contains two parts, `schema` and `uuid`. `schema` is used for
    resolver selection. `uuid` is resolver specific data.
    Ussually it is just uuid number.
    """
    if not uri:
        return

    try:
        schema, data = uri.split(':', 1)
    except ValueError:
        return None

    try:
        return resolvers[schema](uri)
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


def resolver(schema, title=''):
    info = config.DirectiveInfo()

    def wrapper(func):
        resolvers[schema] = func
        resolversTitle[schema] = title or schema

        info.attach(
            config.Action(
                _registerResolver, (schema, func, title),
                discriminator = ('ptah:uri-resolver', schema))
            )

        return func

    return wrapper


def register_uri_resolver(schema, resolver, title='', depth=1):
    """ Register resolver for given schema

    :param schema: Uri schema
    :type schema: string
    :param resolver: Callable object that accept one parameter.

    Resolver interface::

      class Resolver(object):

         def __call__(self, uri):
             return content
    """
    resolvers[schema] = resolver
    resolversTitle[schema] = title or schema

    info = config.DirectiveInfo(depth=depth)
    info.attach(
        config.Action(
            _registerResolver, (schema, resolver, title),
            discriminator = ('ptah:uri-resolver', schema))
        )


def _registerResolver(schema, resolver, title):
    resolvers[schema] = resolver
    resolversTitle[schema] = title or schema


class UriGenerator(object):
    """ Uri Generator

    Example::

       >> uri = UriGenerator('cms+content')

       >> uri()
       'cms+content:f73f3266fa15438e94cca3621a3f2dbc'

    """

    def __init__(self, schema):
        self.schema = schema

    def __call__(self):
        """ Generate new uri using supplied schema """
        return '%s:%s'%(self.schema, uuid.uuid4().get_hex())


@config.addCleanup
def cleanup():
    resolvers.clear()
    resolversTitle.clear()
