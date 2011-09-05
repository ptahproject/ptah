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


class Fieldset(OrderedDict):

    def __init__(self, *args, **kwargs):
        super(Fieldset, self).__init__()

        node = args[0]
        
        self.name = node.name
        self.legend = node.title
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

        self.fieldsets = fieldsets = []

        # Walk through each field, making a widget out of it.
        for fieldset in self.form.fields.fieldsets():
            widgets = []

            for field in fieldset.fields():
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
                    widget = factory(field.node)
                else:
                    factory = getDefaultWidget(field.node)
                    if factory is not None:
                        widget = factory(field.node)

                if widget is None:
                    raise TypeError("Can't find widget for %s"%field)

                # Step 3: Set the prefix for the widget
                name = '%s%s%s'%(prefix, fieldset.prefix, field.name)

                widget.id = name.replace('.', '-')
                widget.name = name
                widget.fieldset = fieldset.name
                widget.fieldname = field.name

                # Step 4: Set the content
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
                widget.__name__ = '%s%s'%(fieldset.prefix, field.name)
                widgets.append(widget)
                self[widget.__name__] = widget

            fieldsets.append(
                {'name': fieldset.name,
                 'legend': fieldset.legend,
                 'widgets': widgets})

    def extract(self, setErrors=True):
        data = {}
        errors = []
        sm = self.request.registry

        for name, widget in self.items():
            if widget.mode == FORM_DISPLAY:
                continue

            value = widget.node.missing
            try:
                value = widget.node.deserialize(widget.extract())
            except colander.Invalid, error:
                error = WidgetError(error, error.msg, widget)
                errors.append(error)
                if setErrors:
                    widget.error = error

            data[widget.__name__] = value
        
        data = self.form.fields.unflatten(data)

        # validate against schemas
        extra_errors = []
        try:
            self.form.fields.validator(None, data)
        except colander.Invalid, error:
            for err in error.children:
                extra_errors.append(err)

            if error.msg is not None:
                extra_errors.append(error)

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
