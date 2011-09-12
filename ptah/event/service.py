""" event service implementation """
from memphis import config


eventTypes = {}

def registerEvent(uuid, name, title='', description=''):
    resolvers[name] = component
    resolversInfo[name] = (title, description)

    info = config.DirectiveInfo()
    info.attach(
        config.Action(None, discriminator = ('ptah.event:type', uuid))
        )
