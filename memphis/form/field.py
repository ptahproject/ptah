import colander
from zope import interface
from pyramid.i18n import get_localizer

from memphis import config
from memphis.form.util import expandPrefix, OrderedDict
from memphis.form.error import Error, WidgetError
from memphis.form.pagelets import FORM_INPUT, FORM_DISPLAY
from memphis.form.interfaces import IForm, IField, IWidget, IWidgets

from directive import getWidget, getDefaultWidget


class Field(object):
    """Field implementation."""
    interface.implements(IField)

    css = ''
    widget = None

    def __init__(self, node, name=None, prefix='', mode=None, readonly=False):
        self.typ = node.typ
        self.node = node
        if name is None:
            name = node.name
        self.name = expandPrefix(prefix) + name
        self.prefix = prefix
        self.mode = mode
        self.readonly = readonly

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.name)


class Fields(OrderedDict):

    def __init__(self, *args, **defaults):
        super(Fields, self).__init__()

        self.schemas = schemas = []

        fields = []
        for arg in args:
            if isinstance(arg, colander._SchemaMeta):
                arg = arg()

            if isinstance(arg, colander.SchemaNode):
                schemas.append(arg)
                for field in arg.children:
                    fields.append((field.name, field))

            elif isinstance(arg, Fields):
                schemas.extend(arg.schemas)
                for form_field in arg.values():
                    fields.append((form_field.name, form_field))

            elif isinstance(arg, Field):
                fields.append((arg.name, arg))

            else:
                raise TypeError("Unrecognized argument type", arg)

        for name, field in fields:
            if isinstance(field, Field):
                form_field = field
            else:
                customDefaults = defaults.copy()
                form_field = Field(field, **customDefaults)
                name = form_field.name

            if name in self:
                raise ValueError("Duplicate name", name)

            self[name] = form_field

    def select(self, *names):
        return self.__class__(*[self[name] for name in names])

    def omit(self, *names):
        return self.__class__(
            *[item for name, item in self.items() if name not in names])


class FieldWidgets(OrderedDict):
    interface.implements(IWidgets)
    config.adapter(IForm, interface.Interface)

    prefix = 'widgets.'
    mode = FORM_INPUT
    errors = ()

    def __init__(self, form, request):
        super(FieldWidgets, self).__init__()

        self.form = form
        self.request = request
        self.localizer = get_localizer(request)

    def update(self):
        content = self.content = self.form.getContent()

        # Create a unique prefix.
        prefix = expandPrefix(self.form.prefix)
        prefix += expandPrefix(self.prefix)
        request = self.request
        params = self.form.getParams()
        context = self.form.getContext()

        sm = self.request.registry

        # Walk through each field, making a widget out of it.
        for field in self.form.fields.values():
            # Step 1: Determine the mode of the widget.
            mode = self.mode
            if field.mode is not None:
                mode = field.mode
            elif field.readonly or getattr(field.node, 'readonly', False):
                mode = FORM_DISPLAY

            # Step 2: Get the widget for the given field.
            widget = None
            factory = field.widget
            if factory is None:
                factory = field.node.widget

            if isinstance(factory, basestring):
                factory = getWidget(factory)

            if callable(factory):
                widget = factory(field.node, field.typ)
            else:
                factory = getDefaultWidget(field.node)
                if factory is not None:
                    widget = factory(field.node, field.typ)

            if widget is None:
                raise TypeError("Can't find widget for %s"%field)

            # Step 3: Set the prefix for the widget
            widget.name = '%s%s'%(prefix, field.name)
            widget.id = widget.name.replace('.', '-')

            # Step 4: Set the content
            widget.context = context
            widget.content = content

            # Step 5: Set the form
            widget.form = self.form

            # Step 6: Set some variables
            widget.params = params
            widget.request = self.request
            widget.localizer = self.localizer

            # Step 7: Set the mode of the widget
            widget.mode = mode

            # Step 8: Update the widget
            widget.update()

            # Step 9:
            widget.addClass(field.css)

            # Step 10: Add the widget to the manager
            widget.__parent__ = self
            widget.__name__ = field.name
            self[field.name] = widget

    def extract(self, setErrors=True):
        data = {}
        sm = self.request.registry
        errors = []
        errorViews = []
        context = self.form.getContext()

        for name, widget in self.items():
            if widget.mode == FORM_DISPLAY:
                continue

            value = widget.node.missing
            try:
                value = widget.node.deserialize(widget.extract())
            except colander.Invalid, error:
                errors.append(error)

            data[widget.__name__] = value

        # validate agains top level SchemaNode
        for node in self.form.fields.schemas:
            try:
                if node.validator:
                    node.validator(node, data)
            except colander.Invalid, error:
                for err in error.children:
                    errors.append(err)

                if error.msg is not None:
                    errors.append(error)

        # call form validation
        self.form.validate(data, errors)

        # prepare errors
        for error in errors:
            widget = self.get(error.node.name)

            if widget is None:
                err = Error(error, error.msg)
            else:
                err = WidgetError(error, error.msg, widget)

            if widget is not None and widget.error is not None:
                continue

            errorViews.append(err)

            if setErrors and widget is not None:
                widget.error = err

        if setErrors:
            self.errors = errorViews

        return data, errorViews
