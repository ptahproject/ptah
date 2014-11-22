""" Form buttons """
import re
import sys
import binascii
from collections import OrderedDict
from ptah.form.field import InputField

AC_DEFAULT = 0
AC_PRIMARY = 1
AC_DANGER = 2
AC_SUCCESS = 3
AC_INFO = 4
AC_WARNING = 4

css = {
    AC_PRIMARY: 'btn-primary',
    AC_DANGER: 'btn-danger',
    AC_SUCCESS: 'btn-success',
    AC_INFO: 'btn-info',
    AC_WARNING: 'brn-warning'}


class Button(InputField):
    """A simple button in a form."""

    klass = 'btn'
    actype = ''

    html_type = 'submit'
    html_attrs = ('id', 'name', 'title', 'lang', 'disabled', 'tabindex',
                  'lang', 'disabled', 'readonly', 'alt', 'accesskey', 'value')

    __staticfuncs__ = InputField.__staticfuncs__ + ('action', 'condition')

    def __init__(self, name='submit', value=None, title=None,
                 action=None, action_name=None,
                 actype=AC_DEFAULT, condition=None, extract=False, **kw):
        self.__dict__.update(kw)

        if value is None:
            value = name.capitalize()

        if isinstance(name, bytes):
            name = name.decode('utf-8')
        name = re.sub('\s', '_', name)

        self.name = name
        self.value = value
        self.title = title
        self.action = action
        self.action_name = action_name
        self.actype = actype
        self.condition = condition
        self.extract = extract
        self.klass = '{0} {1}'.format(self.klass, css.get(self.actype,''))

    def __repr__(self):
        return '<{0} "{1}" : "{2}">'.format(
            self.__class__.__name__, self.name, self.value)

    def __call__(self, context):
        args = []

        if self.extract:
            data, errors = context.extract()
            if errors:
                context.add_error_message(errors)
                return

            args.append(data)

        if self.action_name is not None:
            return getattr(context, self.action_name)(*args)
        elif self.action is not None:
            return self.action(context, *args)
        else:
            raise TypeError("Action is not specified")

    def bind(self, request, prefix, params, context):
        return self.cls(
            id = str(prefix + self.name).replace('.', '-'),
            name = str(prefix + self.name),
            params = params,
            request = request,
            context = context)

    def activated(self):
        return self.params.get(self.name, None) is not None


class Buttons(OrderedDict):
    """Form buttons manager."""

    def __init__(self, *args):
        super(Buttons, self).__init__()

        buttons = []
        for arg in args:
            if isinstance(arg, Buttons):
                buttons += arg.values()
            else:
                buttons.append(arg)

        self.add(*buttons)

    def add(self, *btns):
        """Add buttons to this manager."""
        for btn in btns:
            if btn.name in self:
                raise ValueError("Duplicate name", btn.name)

            self[btn.name] = btn

    def add_action(self, value, **kwargs):
        """Add action to this manager."""
        # Add the value to button constructor keyword arguments
        kwargs['value'] = value
        if 'name' not in kwargs:
            kwargs['name'] = create_btn_id(value)

        button = Button(**kwargs)

        self.add(button)

        return button

    def __add__(self, other):
        return self.__class__(self, other)


class Actions(OrderedDict):
    """Form actions manager."""

    prefix = 'buttons.'

    def __init__(self, form, request):
        self.form = form
        self.request = request

        super(Actions, self).__init__()

    def update(self):
        form = self.form
        params = form.form_params()

        # Create a unique prefix.
        prefix = '%s%s' % (form.prefix, self.prefix)

        # Walk through each node, making a widget out of it.
        for field in self.form.buttons.values():
            if field.condition and not field.condition(form):
                continue

            self[field.name] = field.bind(self.request, prefix, params, form)

    def execute(self):
        result = None
        executed = False
        for action in self.values():
            if action.activated():
                executed = True
                result = action(self.form)

        if executed:
            self.clear()
            self.update()

        return result


_identifier = re.compile('[A-Za-z][a-zA-Z0-9_]*$')


def create_btn_id(name):
    if _identifier.match(name):
        return str(name).lower()
    return binascii.hexlify(name.encode('utf-8'))


def _button(f_locals, value, kwargs):
    # install buttons manager
    buttons = f_locals.get('buttons')
    if buttons is None:
        buttons = Buttons()
        f_locals['buttons'] = buttons

    # create button
    btn = buttons.add_action(value, **kwargs)

    def createHandler(func):
        btn.action_name = func.__name__
        btn.cls.action_name = func.__name__
        return func

    return createHandler


def button(value, **kwargs):
    """ Register new form button.

    :param value: Button value. it is beeing used for html form generations.
    :param kwargs: Keyword arguments

    .. code-block:: python

      class CustomForm(form.Form):

          field = form.Fieldset()

          @form.button('Cancel')
          def handle_cancel(self):
              ...
    """
    return _button(sys._getframe(1).f_locals, value, kwargs)


def button2(value, **kwargs):
    """ Register new form button.

    :param value: Button value. it is beeing used for html form generations.
    :param kwargs: Keyword arguments

    .. code-block:: python

      class CustomForm(form.Form):

          field = form.Fieldset()

          @form.button2('Cancel')
          def handle_cancel(self, data):
              ...
    """
    kwargs['extract'] = True
    return _button(sys._getframe(1).f_locals, value, kwargs)
