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
"""Button and Button Manager implementation

$Id: button.py 11790 2011-01-31 00:41:45Z fafhrd91 $
"""
__docformat__ = "reStructuredText"
import sys
import zope.event
import zope.interface
import zope.schema
import zope.component

from zope.interface import adapter
from zope.schema.fieldproperty import FieldProperty

from memphis import config
from memphis.form import action, interfaces, util

from memphis.form.browser import submit


class Button(zope.schema.Field):
    """A simple button in a form."""
    zope.interface.implements(interfaces.IButton)

    accessKey = None #FieldProperty(interfaces.IButton['accessKey'])
    actionFactory = None #FieldProperty(interfaces.IButton['actionFactory'])

    def __init__(self, *args, **kwargs):
        # Provide some shortcut ways to specify the name
        if args:
            kwargs['__name__'] = args[0]
            args = args[1:]
        if 'name' in kwargs:
            kwargs['__name__'] = kwargs['name']
            del kwargs['name']
        # Extract button-specific arguments
        self.accessKey = kwargs.pop('accessKey', None)
        self.condition = kwargs.pop('condition', None)
        # Initialize the button
        super(Button, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<%s %r %r>' %(
            self.__class__.__name__, self.__name__, self.title)


class Buttons(util.SelectionManager):
    """Button manager."""
    zope.interface.implements(interfaces.IButtons)

    managerInterface = interfaces.IButtons
    prefix = 'buttons'

    def __init__(self, *args):
        buttons = []
        for arg in args:
            if zope.interface.interfaces.IInterface.providedBy(arg):
                for name, button in zope.schema.getFieldsInOrder(arg):
                    if interfaces.IButton.providedBy(button):
                        buttons.append((name, button))
            elif self.managerInterface.providedBy(arg):
                buttons += arg.items()
            elif interfaces.IButton.providedBy(arg):
                if not arg.__name__:
                    arg.__name__ = util.createId(arg.title)
                buttons.append((arg.__name__, arg))
            else:
                raise TypeError("Unrecognized argument type", arg)
        keys = []
        seq = []
        byname = {}
        for name, button in buttons:
            keys.append(name)
            seq.append(button)
            byname[name] = button

        self._data_keys = keys
        self._data_values = seq
        self._data = byname


class Handlers(object):
    """Action Handlers for a Button-based form."""
    zope.interface.implements(interfaces.IButtonHandlers)

    def __init__(self):
        self._registry = adapter.AdapterRegistry()
        self._handlers = ()

    def addHandler(self, button, handler):
        """See interfaces.IButtonHandlers"""
        # Create a specification for the button
        buttonSpec = util.getSpecification(button)
        if isinstance(buttonSpec, util.classTypes):
            buttonSpec = zope.interface.implementedBy(buttonSpec)
        # Register the handler
        self._registry.register(
            (buttonSpec,), interfaces.IButtonHandler, '', handler)
        self._handlers += ((button, handler),)

    def getHandler(self, button):
        """See interfaces.IButtonHandlers"""
        buttonProvided = zope.interface.providedBy(button)
        return self._registry.lookup1(buttonProvided, interfaces.IButtonHandler)

    def copy(self):
        """See interfaces.IButtonHandlers"""
        handlers = Handlers()
        for button, handler in self._handlers:
            handlers.addHandler(button, handler)
        return handlers

    def __add__(self, other):
        """See interfaces.IButtonHandlers"""
        if not isinstance(other, Handlers):
            raise NotImplementedError
        handlers = self.copy()
        for button, handler in other._handlers:
            handlers.addHandler(button, handler)
        return handlers

    def __repr__(self):
        return '<Handlers %r>' %[handler for button, handler in self._handlers]


class Handler(object):
    zope.interface.implements(interfaces.IButtonHandler)

    def __init__(self, button, func):
        self.button = button
        self.func = func

    def __call__(self, form, action):
        return self.func(form, action)

    def __repr__(self):
        return '<%s for %r>' %(self.__class__.__name__, self.button)


def handler(button):
    """A decorator for defining a success handler."""
    def createHandler(func):
        handler = Handler(button, func)
        frame = sys._getframe(1)
        f_locals = frame.f_locals
        handlers = f_locals.setdefault('handlers', Handlers())
        handlers.addHandler(button, handler)
        return handler
    return createHandler


def buttonAndHandler(title, **kwargs):
    # Add the title to button constructor keyword arguments
    kwargs['title'] = title
    # Extract directly provided interfaces:
    provides = kwargs.pop('provides', ())
    # Create button and add it to the button manager
    button = Button(**kwargs)
    zope.interface.alsoProvides(button, provides)
    frame = sys._getframe(1)
    f_locals = frame.f_locals
    buttons = f_locals.setdefault('buttons', Buttons())
    f_locals['buttons'] += Buttons(button)
    # Return the handler decorator
    return handler(button)


class ButtonAction(action.Action, submit.SubmitWidget):
    zope.interface.implements(interfaces.IButtonAction)
    config.adapts(None, interfaces.IButton)

    def __init__(self, request, field):
        action.Action.__init__(self, request, field.title, field.__name__)
        submit.SubmitWidget.__init__(self, field, request)

    @property
    def accesskey(self):
        return self.field.accessKey


class ButtonActions(action.Actions):
    config.adapts(
        interfaces.IButtonForm,
        zope.interface.Interface,
        zope.interface.Interface)

    def update(self, arguments):
        self.arguments = arguments

        # Create a unique prefix.
        prefix = util.expandPrefix(self.form.prefix)
        prefix += util.expandPrefix(self.form.buttons.prefix)
        # Walk through each field, making an action out of it.
        uniqueOrderedKeys = []
        for name, button in self.form.buttons.items():
            # Step 1: Only create an action for the button, if the condition is
            #         fulfilled.
            if button.condition is not None and not button.condition(self.form):
                continue
            # Step 2: Get the action for the given button.
            newButton = True
            if name in self._data:
                buttonAction = self._data[name]
                newButton = False
            elif button.actionFactory is not None:
                buttonAction = button.actionFactory(self.request, button)
            else:
                buttonAction = zope.component.getMultiAdapter(
                    (self.request, button), interfaces.IButtonAction)
            # Step 3: Set the name on the button
            buttonAction.name = prefix + name
            
            # Step 5: Set the form
            buttonAction.form = self.form
            if not interfaces.IFormAware.providedBy(buttonAction):
                zope.interface.alsoProvides(buttonAction, interfaces.IFormAware)

            # Step 6: Update the new action
            buttonAction.update()
            #zope.event.notify(AfterWidgetUpdateEvent(buttonAction))

            # Step 7: Add the widget to the manager
            uniqueOrderedKeys.append(name)
            if newButton:
                self._data_values.append(buttonAction)
                self._data[name] = buttonAction
                buttonAction.__parent__ = self
                buttonAction.__name__ = name
            # allways ensure that we add all keys and keep the order given from
            # button items
            self._data_keys = uniqueOrderedKeys


class ButtonActionHandler(action.ActionHandlerBase):
    config.adapts(
        interfaces.IHandlerForm,
        zope.interface.Interface,
        zope.interface.Interface,
        ButtonAction)

    def __call__(self):
        handler = self.form.handlers.getHandler(self.action.field)
        # If no handler is found, then that's okay too.
        if handler is None:
            return
        return handler(self.form, self.action)
