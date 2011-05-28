""" view action implementation """
from pyramid import url
from zope import interface

from memphis import config
from memphis.view.interfaces import IAction


def registerActions(*actions):
    for data in actions:
        registerAction(*data)


def registerAction(name='', context=None,
                   title = u'', description = u'', weight = 0):
    action = Action(name, title, description, weight)

    config.registerAdapter(action, (context,), IAction, name)


class Action(object):
    interface.implements(IAction)

    def __init__(self, name, title, description, weight):
        self.name = name
        self.title = title
        self.description = description
        self.weight = weight

    def url(self, context, request):
        return '%s%s'%(url.resource_url(context, request), self.name)
