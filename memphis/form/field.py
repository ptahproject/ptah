import colander
from zope import interface
from collections import OrderedDict
from pyramid.i18n import get_localizer

from memphis import config
from memphis.form.error import Error, WidgetError
from memphis.form.pagelets import FORM_INPUT, FORM_DISPLAY
from memphis.form.interfaces import \
    IForm, IField, IWidget, IWidgets, IDataManager

from directive import getWidget, getDefaultWidget


class Field(object):
    """Field implementation."""
    interface.implements(IField)

    css = ''
    widget = None

    def __init__(self, node, name=None, mode=None, readonly=None):
        self.typ = node.typ
        self.node = node
        if name is None:
            name = node.name
        self.name = name
        self.mode = mode

        if readonly is None:
            readonly = getattr(node, 'readonly', False)
        self.readonly = readonly

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.name)


class Fieldset(OrderedDict):

    def __init__(self, *args, **kwargs):
        super(Fieldset, self).__init__()

        node = args[0]

        if 'name' in kwargs:
            name = kwargs.pop('name')
        else:
            name = node.name

        if 'legend' in kwargs:
            legend = kwargs.pop('legend')
        else:
            legend = node.title

        self.name = name
        self.legend = legend
        self.names = []
        self.schemas = []
        self.prefix = '%s.'%self.name if self.name else ''
        self.lprefix = len(self.prefix)

        self.append(node, **kwargs)
        self.append(*args[1:], **kwargs)

    def fields(self):
        for field in self.values():
            if isinstance(field, Field):
                yield field

    def fieldsets(self):
        yield self

        for fieldset in self.values():
            if isinstance(fieldset, Fieldset):
                yield fieldset

    def unflatten(self, appdata):
        data = dict((key[self.lprefix:], appdata[key])
                    for key in appdata if key in self.names)

        for name, fieldset in self.items():
            if isinstance(fieldset, Fieldset):
                data[name] = fieldset.unflatten(appdata)

        return data

    def append(self, *args, **kwargs):
        omit = kwargs.get('omit', ())
        select = kwargs.get('select', ())

        for node in args:
            self.schemas.append(node)

            if isinstance(node, colander.SchemaNode):
                for snode in node.children:
                    if omit and snode.name in omit:
                        continue
                    if select and snode.name not in select:
                        continue

                    self.names.append('%s%s'%(self.prefix, snode.name))

                    if isinstance(snode.typ, colander.Mapping):
                        self[snode.name] = Fieldset(snode)
                    else:
                        field = Field(snode)
                        if field.name in self:
                            raise ValueError("Duplicate name", field.name)
                        self[field.name] = field

            elif isinstance(node, Fieldset):
                self[node.name] = node
                self.names.append('%s%s'%(self.prefix, node.name))

            else:
                raise TypeError("Unrecognized argument type", arg)

    def select(self, *names):
        return self.__class__(select=names, *self.schemas)

    def omit(self, *names):
        return self.__class__(omit=names, *self.schemas)

    def validator(self, node, appstruct):
        for schema in self.schemas:
            if schema.validator is not None:
                schema.validator(schema, appstruct)


class Fields(Fieldset):

    def __init__(self, *args, **kwargs):
        super(Fields, self).__init__(
            colander.SchemaNode(colander.Mapping()))

        for arg in args:
            if isinstance(arg, colander._SchemaMeta):
                arg = arg()

            if isinstance(arg, (Fieldset, colander.SchemaNode)):
                self.append(arg, **kwargs)

            else:
                raise TypeError("Unrecognized argument type", arg)


class FieldWidgets(OrderedDict):
    interface.implements(IWidgets)

    prefix = 'widgets.'
    mode = FORM_INPUT
    errors = ()
    content = None
    fieldsets = ()

    def __init__(self, fields, form, request):
        super(FieldWidgets, self).__init__()

        self.fields = fields
        self.form = form
        self.request = request
        self.localizer = get_localizer(request)

    def update(self):
        content = self.form.getContent()
        if content is not None:
            self.content = content = IDataManager(content)
                
        # Create a unique prefix.
        prefix = '%s%s'%(self.form.prefix, self.prefix)

        sm = config.registry
        params = self.form.getParams()

        self.fieldsets = fieldsets = []

        # Walk through each field, making a widget out of it.
        for fieldset in self.fields.fieldsets():
            widgets = []

            for field in fieldset.fields():
                # Step 1: Get the widget for the given field.
                widget = None
                factory = field.widget
                if factory is None:
                    factory = field.node.widget

                if isinstance(factory, basestring):
                    factory = getWidget(factory)

                if callable(factory):
                    widget = factory(field.node)
                else:
                    factory = getDefaultWidget(field.node)
                    if factory is not None:
                        widget = factory(field.node)

                if widget is None:
                    raise TypeError("Can't find widget for %s"%field)

                # Step 2: Set the prefix for the widget
                name = '%s%s'%(fieldset.prefix, field.name)

                widget.id = ('%s%s'%(prefix, name)).replace('.', '-')
                widget.name = name
                widget.fieldset = fieldset.name
                widget.fieldname = field.name

                # Step 3: Set the content
                if content is not None:
                    widget.content = content.dataset(fieldset.name)

                # Step 4: Set the form
                widget.form = self.form

                # Step 5: Set some variables
                widget.params = params
                widget.request = self.request
                widget.localizer = self.localizer

                # Step 6: Set the mode of the widget
                if field.mode is not None:
                    widget.mode = field.mode
                elif field.readonly:
                    widget.mode = FORM_DISPLAY
                else:
                    widget.mode = self.mode

                # Step 7: Update the widget
                widget.update()

                # Step 8:
                widget.addClass(field.css)

                # Step 9: Add the widget to the manager
                widget.__name__ = name
                widget.__parent__ = self
                widgets.append(widget)
                self[widget.__name__] = widget

            fieldsets.append(
                {'name': fieldset.name,
                 'legend': fieldset.legend,
                 'widgets': widgets})

    def extract(self, setErrors=True):
        data = {}
        errors = []
        sm = config.registry

        for name, widget in self.items():
            if widget.mode == FORM_DISPLAY:
                continue

            value = widget.node.missing
            try:
                value = widget.deserialize(widget.extract())
            except colander.Invalid, error:
                error = WidgetError(error, error.msg, widget)
                errors.append(error)
                if setErrors:
                    widget.error = error

            data[widget.__name__] = value

        data = self.fields.unflatten(data)

        # validate against schemas
        extra_errors = []
        try:
            self.fields.validator(None, data)
        except colander.Invalid, error:
            if error.msg is not None:
                extra_errors.append(error)

            extra_errors.extend(error.children)

        # form validation
        self.form.validate(data, extra_errors)

        # prepare errors
        for error in extra_errors:
            widget = self.get(error.node.name)
            if widget is None:
                err = Error(error, error.msg)
            else:
                err = WidgetError(error, error.msg, widget)

            if widget is not None and widget.error is not None:
                continue

            errors.append(err)

            if setErrors and widget is not None:
                widget.error = err

        self.errors = errors
        return data, errors
