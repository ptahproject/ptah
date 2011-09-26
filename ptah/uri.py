""" uri resolver """
import uuid
from memphis import config

resolvers = {}
resolversInfo = {}


def resolve(uri):
    """ Resolve uri, return resolved object.

    Uri contains two parts, `schema` and `uuid`. `schema` is used for 
    resolver selection. `uuid` is resolver specific data.
    Ussually it is just uuid number.
    """
    if not uri:
        return

    try:
        schema, uuid = uri.split(':', 1)
    except ValueError:
        return None

    try:
        return resolvers[schema](uri)
    except KeyError:
        pass

    return None


def extractUriSchema(uri):
    """ Extract schema of given uri """
    if uri:
        try:
            schema, uuid = uri.split(':', 1)
            return schema
        except:
            pass

    return None


def registerResolver(schema, resolver, title='', description='', depth=1):
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
    resolversInfo[schema] = (title, description)

    info = config.DirectiveInfo(depth=depth)
    info.attach(
        config.Action(
            _registerResolver, (schema, resolver, title, description),
            discriminator = ('ptah:uri-resolver', schema))
        )


def _registerResolver(schema, resolver, title, description):
    resolvers[schema] = resolver
    resolversInfo[schema] = (title, description)


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
    resolversInfo.clear()
