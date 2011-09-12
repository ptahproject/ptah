""" uri resolver """
from memphis import config

resolvers = {}
resolversInfo = {}

def resolve(uri):
    name = uri.split('://', 1)[0]
    
    resolver = resolvers.get(name)
    if resolver is not None:
        return resolver(uri)

    return None


def registerResolver(name, component, title='', description=''):
    resolvers[name] = component
    resolversInfo[name] = (title, description)

    info = config.DirectiveInfo()
    info.attach(
        config.Action(None, discriminator = ('ptah:uri-resolver', name))
        )
