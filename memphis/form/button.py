""" Button and Button Manager implementation """
import sys, re
import colander
from zope import interface
from zope.component import getSiteManager

from memphis import config
from memphis.form.field import Field
from memphis.form.util import createId, expandPrefix, OrderedDict
from memphis.form.interfaces import IForm, IButton, IActions, IWidget

AC_DEFAULT = 0
AC_PRIMARY = 1
AC_DANGER = 2
AC_SUCCESS = 3
AC_INFO = 4


class Button(Field):
    """A simple button in a form."""
    interface.implements(IButton)

    description = ''

    def __init__(self, name='submit', title=None, type='submit', value=None,
                 disabled=False, accessKey = None,
                 action=None, actype=AC_DEFAULT):
        if title is None:
            title = name.capitalize()
        name = re.sub(r'\s', '_', name)
        if value is None:
            value = name

        self.name = name
        self.typ = colander.Str()

        self.__name__ = name

        self.title = title
        self.type = type
        self.value = value
        self.disabled = disabled
        self.accessKey = accessKey
        self.action = action
        self.required = False
        self.actype = actype

    def __repr__(self):
        return '<%s %r %r>' %(
            self.__class__.__name__, self.name, self.title)

    def __call__(self, form):
        return self.action(form)


class Buttons(OrderedDict):
    """Button manager."""

    prefix = 'buttons'

    def __init__(self, *args):
        super(Buttons, self).__init__()

        buttons = []
        for arg in args:
            if isinstance(arg, Buttons):
                buttons += arg.items()
            else:
                buttons.append((arg.name, arg))

        for name, button in buttons:
            self[name] = button


class Actions(OrderedDict):
    """ Widget manager for Buttons """
    config.adapts(IForm, interface.Interface)
    interface.implementsOnly(IActions)

    prefix = 'buttons.'

    def __init__(self, form, request):
        super(Actions, self).__init__()

        self.form = form
        self.request = request

    def update(self):
        content = self.content = self.form.getContent()

        # Create a unique prefix.
        prefix = expandPrefix(self.form.prefix)
        prefix += expandPrefix(self.prefix)
        request = self.request
        params = self.form.getRequestParams()
        context = self.form.getContext()

        sm = getSiteManager()

        # Walk through each node, making a widget out of it.
        for field in self.form.buttons.values():
            # Step 2: Get the widget for the given field.
            shortName = field.name

            widget = None
            factory = field.widget
            if isinstance(factory, basestring):
                widget = sm.queryMultiAdapter(
                    (field, field.typ), IWidget, name=factory)
            elif callable(factory):
                widget = factory(field, field.node)
            else:
                widget = sm.queryMultiAdapter((field, field.typ), IWidget)

            # Step 3: Set the prefix for the widget
            widget.name = str(prefix + shortName)
            widget.id = str(prefix + shortName).replace('.', '-')

            # Step 4: Set the content
            widget.context = context
            widget.content = content

            # Step 5: Set the form
            widget.form = self.form

            # Step 6: Set some variables
            widget.params = params

            # Step 8: Update the widget
            widget.update()

            # Step 9: Add the widget to the manager
            widget.__parent__ = self
            widget.__name__ = shortName
            self[shortName] = widget

    def execute(self):
        for action in self.values():
            val = action.extract()
            if val is not colander.null:
                action.node(self.form)


def button(title, **kwargs):
    # Add the title to button constructor keyword arguments
    kwargs['title'] = title
    if 'name' not in kwargs:
        kwargs['name'] = createId(title)

    # Extract directly provided interfaces:
    provides = kwargs.pop('provides', ())

    # Create button and add it to the button manager
    button = Button(**kwargs)
    interface.alsoProvides(button, provides)

    # install buttons manager
    frame = sys._getframe(1)
    f_locals = frame.f_locals
    buttons = f_locals.setdefault('buttons', Buttons())
    f_locals['buttons'] += Buttons(button)

    def createHandler(func):
        button.action = func
        return func

    return createHandler
