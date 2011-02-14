from pyramid import url
from zope import interface
from memphis.view.interfaces import IAction


class Action(object):
    interface.implements(IAction)

    name = ''
    title = ''
    description = ''
    
    def __init__(self, context):
        self.context = context

    def url(self, request):
        return '%s%s'%(url.resource_url(self.context, request), self.name)
