""" uri resolver """
import uuid
from memphis import config

resolvers = {}
resolversInfo = {}


def resolve(uri):
    type, uuid = uri.split('://', 1)

    try:
        return resolvers[type](uri)
    except KeyError:
        pass

    return None


def registerResolver(type, component, title='', description=''):
    resolvers[type] = component
    resolversInfo['%s://'%type] = (title, description)

    info = config.DirectiveInfo()
    info.attach(
        config.Action(None, discriminator = ('ptah:uri-resolver',type))
        )


class UUIDGenerator(object):

    def __init__(self, type):
        self.type = type

    def __call__(self):
        return '%s://%s'%(self.type, uuid.uuid4().get_hex())
