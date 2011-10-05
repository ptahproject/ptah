""" Button and Button Manager implementation """
import sys, re
from zope import interface
from collections import OrderedDict
from pyramid.i18n import get_localizer

from memphis import config, view
from memphis.form.interfaces import IForm, IButton, IActions, IWidget

from interfaces import null, required


AC_DEFAULT = 0
AC_PRIMARY = 1
AC_DANGER = 2
AC_SUCCESS = 3
AC_INFO = 4


class Button(object):
    """A simple button in a form."""
    interface.implements(IButton)

    template = view.template("memphis.form:templates/submit.pt")

    def __init__(self, name='submit', title=None, type='submit', value=None,
                 disabled=False, accessKey = None, action=None, actionName=None,
                 actype=AC_DEFAULT, condition=None):

        if title is None:
            title = name.capitalize()
        name = re.sub(r'\s', '_', name)
        if value is None:
            value = name

        self.name = name

        self.__name__ = name

        self.title = title
        self.type = type
        self.value = value
        self.disabled = disabled
        self.accessKey = accessKey
        self.action = action
        self.actionName = actionName
        self.required = False
        self.actype = actype
        self.condition = condition

    def __repr__(self):
        return '<%s %r %r>' %(
            self.__class__.__name__, self.name, self.title)

    def __call__(self, form):
        if self.actionName is not None:
            return getattr(form, self.actionName)()
        else:
            self.action(form)


class SubmitWidget(view.View):
    """A simple button of a form."""

    klass = u'btn submit-widget'
    template = view.template("memphis.form:templates/submit.pt")

    lang = None
    readonly = None
    alt = None
    accesskey = None
    disabled = None
    tabindex = None

    def __init__(self, node, request):
        self.node = node
        self.context = node
        self.request = request

    def addClass(self, klass):
        if not self.klass:
            self.klass = klass
        else:
            if klass not in self.klass:
                self.klass = u'%s %s'%(self.klass, klass)

    def update(self):
        self.value = self.node.title
        if self.node.actype == AC_PRIMARY:
            self.addClass('primary')
        elif self.node.actype == AC_DANGER:
            self.addClass('danger')
        elif self.node.actype == AC_SUCCESS:
            self.addClass('success')
        elif self.node.actype == AC_INFO:
            self.addClass('info')

    def extract(self, default=None):
        return self.params.get(self.name, default)

    def render(self):
        return self.template(context = self, request = self.request)


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

    def __add__(self, other):
        return self.__class__(self, other)


class Actions(OrderedDict):
    """ Widget manager for Buttons """
    config.adapter(IForm, interface.Interface)
    interface.implementsOnly(IActions)

    prefix = 'buttons.'

    def __init__(self, form, request):
        super(Actions, self).__init__()

        self.form = form
        self.request = request
        self.localizer = get_localizer(request)

    def update(self):
        form = self.form
        content = self.content = form.getContent()
        params = form.getParams()
        request = self.request
        registry = config.registry

        # Create a unique prefix.
        prefix = '%s%s'%(form.prefix, self.prefix)

        # Walk through each node, making a widget out of it.
        for field in self.form.buttons.values():
            if field.condition and not field.condition(form):
                continue

            # Step 2: Get the widget for the given field.
            shortName = field.name

            widget = SubmitWidget(field, request)

            # Step 3: Set the prefix for the widget
            widget.name = str(prefix + shortName)
            widget.id = str(prefix + shortName).replace('.', '-')

            # Step 4: Set the content
            widget.content = content
            widget.value = field.value

            # Step 5: Set the form
            widget.form = self.form

            # Step 6: Set some variables
            widget.params = params
            widget.request = self.request
            widget.localizer = self.localizer

            # Step 8: Update the widget
            widget.update()

            # Step 9: Add the widget to the manager
            widget.__parent__ = self
            widget.__name__ = shortName
            self[shortName] = widget

    def execute(self):
        executed = False
        for action in self.values():
            val = action.extract()
            if val is not None: #null:
                executed = True
                action.node(self.form)

        if executed:
            self.clear()
            self.update()


_identifier = re.compile('[A-Za-z][a-zA-Z0-9_]*$')

def createId(name):
    if _identifier.match(name):
        return str(name).lower()
    return name.encode('utf-8').encode('hex')


def button(title, **kwargs):
    # Add the title to button constructor keyword arguments
    kwargs['title'] = title
    if 'name' not in kwargs:
        kwargs['name'] = createId(title)

    # Create button and add it to the button manager
    button = Button(**kwargs)

    # install buttons manager
    f_locals = sys._getframe(1).f_locals

    buttons = f_locals.get('buttons')
    if buttons is None:
        f_locals['buttons'] = Buttons(button)
    else:
        buttons[button.name] = button

    def createHandler(func):
        button.actionName = func.__name__
        return func

    return createHandler
