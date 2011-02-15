""" zca configuration """
from zope.component.event import objectEventNotify

from memphis.config import api
from memphis.config.directives import action


action(api.registerHandler, objectEventNotify)
