##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Form Framework Action Implementation

$Id: action.py 11759 2011-01-29 15:20:03Z fafhrd91 $
"""
__docformat__ = "reStructuredText"
import zope.interface
import zope.component

from memphis.form import interfaces, util


class ActionEvent(object):
    zope.interface.implements(interfaces.IActionEvent)

    def __init__(self, action):
        self.action = action

    def __repr__(self):
        return '<%s for %r>' %(self.__class__.__name__, self.action)


class ActionErrorOccurred(ActionEvent):
    """An event telling the system that an error occurred during action
    execution."""
    zope.interface.implements(interfaces.IActionErrorEvent)

    def __init__(self, action, error):
        super(ActionErrorOccurred, self).__init__(action)
        self.error = error


class ActionSuccessful(ActionEvent):
    """An event signalizing that an action has been successfully executed."""


class Action(object):
    """Action class."""
    zope.interface.implements(interfaces.IAction)

    __name__ = __parent__ = None

    def __init__(self, request, title, name=None):
        self.request = request
        self.title = title
        if name is None:
            name = util.createId(title)
        self.name = name

    def isExecuted(self, arguments):
        return self.name in arguments

    def __repr__(self):
        return '<%s %r %r>' % (self.__class__.__name__, self.name, self.title)


class Actions(util.Manager):
    """Action manager class."""
    zope.interface.implementsOnly(interfaces.IActions)

    __name__ = __parent__ = None

    def __init__(self, form, request, content):
        super(Actions, self).__init__()
        self.form = form
        self.request = request
        self.content = content

    @property
    def executedActions(self):
        return [action for action in self.values()
                if action.isExecuted(self.arguments)]

    def update(self, arguments):
        """See memphis.form.interfaces.IActions."""
        self.arguments = arguments

    def execute(self):
        """See memphis.form.interfaces.IActions."""
        sm = zope.component.getSiteManager()

        for action in self.executedActions:
            handler = sm.queryMultiAdapter(
                (self.form, self.request, self.content, action),
                interface=interfaces.IActionHandler)
            if handler is not None:
                try:
                    result = handler()
                except interfaces.ActionExecutionError, error:
                    zope.event.notify(ActionErrorOccurred(action, error))
                else:
                    zope.event.notify(ActionSuccessful(action))
                    return result

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.__name__)


class ActionHandlerBase(object):
    """Action handler base adapter."""

    zope.interface.implements(interfaces.IActionHandler)

    def __init__(self, form, request, content, action):
        self.form = form
        self.request = request
        self.content = content
        self.action = action
