""" uri resolver """
from memphis import config

resolvers = {}
resolversInfo = {}


def resolve(uri):
    type, data = uri.split('://', 1)
    subtype, uuid = data.split(':', 1)

    try:
        typeresolvers = resolvers[type]
        if None in typeresolvers:
            return typeresolvers[None](uuid)

        return typeresolvers[subtype](uuid)
    except KeyError:
        pass

    return None


def registerResolver(type, subtype, component, title='', description=''):
    typeresolvers = resolvers.setdefault(type, {})
    typeresolvers[subtype] = component
    resolversInfo['%s://%s'%(type, subtype)] = (title, description)

    info = config.DirectiveInfo()
    info.attach(
        config.Action(None, discriminator = ('ptah:uri-resolver',type,subtype))
        )
