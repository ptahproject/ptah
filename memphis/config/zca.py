""" 

$Id: zca.py 4723 2011-02-03 02:05:21Z nikolay $
"""
from zope.component.event import objectEventNotify

from memphis.config import api
from memphis.config.directives import action


action(api.registerHandler, objectEventNotify)
