""" Button and Button Manager implementation """
import sys, re
import colander
from zope import interface
from zope.component import getSiteManager
from memphis import config
from memphis.form import util
from memphis.form.field import Field
from memphis.form.interfaces import IForm, IButton, IActions, IWidget, NO_VALUE


class Button(Field):
    """A simple button in a form."""
    interface.implements(IButton)

    def __init__(self, name='submit', title=None, type='submit', value=None,
                 disabled=False, accessKey = None, 
                 action=None, primary=False):
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
        self.primary = primary

    def __repr__(self):
        return '<%s %r %r>' %(
            self.__class__.__name__, self.name, self.title)

    def __call__(self, form):
        return self.action(form)


class Buttons(util.SelectionManager):
    """Button manager."""

    prefix = 'buttons'

    def __init__(self, *args):
        buttons = []
        for arg in args:
            if isinstance(arg, Buttons):
                buttons += arg.items()
            else:
                buttons.append((arg.name, arg))

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


class Actions(util.Manager):
    """ Widget manager for Buttons """
    config.adapts(IForm, interface.Interface)
    interface.implementsOnly(IActions)

    prefix = 'buttons.'

    def __init__(self, form, request):
        super(Actions, self).__init__()
        self.form = form
        self.request = request

    def update(self):
        self._data = {}
        self._data_values = []
        content = self.content = self.form.getContent()

        # Create a unique prefix.
        prefix = util.expandPrefix(self.form.prefix)
        prefix += util.expandPrefix(self.prefix)
        request = self.request
        params = self.form.getRequestParams()
        context = self.form.getContext()

        sm = getSiteManager()

        # Walk through each field, making a widget out of it.
        uniqueOrderedKeys = []
        for field in self.form.buttons.values():
            # Step 2: Get the widget for the given field.
            shortName = field.name

            widget = None
            factory = field.widgetFactory
            if isinstance(factory, basestring):
                widget = sm.queryMultiAdapter(
                    (field, field.typ, request), IWidget, name=factory)
            elif callable(factory):
                widget = factory(field.field, request)

            if widget is None:
                widget = sm.getMultiAdapter(
                    (field.field, request),interfaces.IDefaultWidget)

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
            uniqueOrderedKeys.append(shortName)

            widget.__parent__ = self
            widget.__name__ = shortName

            self._data_values.append(widget)
            self._data[shortName] = widget
            self._data_keys = uniqueOrderedKeys

    def execute(self):
        for action in self.values():
            val = action.extract()
            if val is not NO_VALUE:
                action.field(self.form)


def button(title, **kwargs):
    # Add the title to button constructor keyword arguments
    kwargs['title'] = title
    if 'name' not in kwargs:
        kwargs['name'] = util.createId(title)

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
