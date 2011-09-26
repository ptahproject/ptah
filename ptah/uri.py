""" uri resolver """
import uuid
from memphis import config

resolvers = {}
resolversInfo = {}


def resolve(uri):
    if not uri:
        return

    try:
        type, uuid = uri.split(':', 1)
    except ValueError:
        return None

    try:
        return resolvers[type](uri)
    except KeyError:
        pass

    return None


def extractUriType(uri):
    if uri:
        try:
            type, uuid = uri.split(':', 1)
            return type
        except:
            pass

    return None


def registerResolver(schema, resolver, title='', description='', depth=1):
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


class UUIDGenerator(object):

    def __init__(self, type):
        self.type = type

    def __call__(self):
        return '%s:%s'%(self.type, uuid.uuid4().get_hex())


@config.addCleanup
def cleanup():
    resolvers.clear()
    resolversInfo.clear()
