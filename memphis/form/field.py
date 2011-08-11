"""Field Implementation"""
import zope.component
import zope.interface
import zope.schema.interfaces
from zope import interface
from zope.component import getSiteManager

from memphis import config
from memphis.form import interfaces, util
from memphis.form.error import \
    Errors, WidgetError, MultipleErrors, ErrorViewSnippet


class Field(object):
    """Field implementation."""
    interface.implements(interfaces.IField)

    widgetFactory = ''

    def __init__(self, field, name=None, prefix='', mode=None, interface=None):
        self.field = field
        if name is None:
            name = field.__name__
        self.__name__ = util.expandPrefix(prefix) + name
        self.prefix = prefix
        self.mode = mode
        if interface is None:
            interface = field.interface
        self.interface = interface

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.__name__)


def _initkw(keepReadOnly=(), omitReadOnly=False, **defaults):
    return keepReadOnly, omitReadOnly, defaults


class Fields(util.SelectionManager):
    """Fields manager."""
    interface.implements(interfaces.IFields)
    managerInterface = interfaces.IFields

    def __init__(self, *args, **kw):
        keepReadOnly, omitReadOnly, defaults = _initkw(**kw)

        fields = []
        for arg in args:
            if isinstance(arg, interface.interface.InterfaceClass):
                for name, field in zope.schema.getFieldsInOrder(arg):
                    fields.append((name, field, arg))

            elif zope.schema.interfaces.IField.providedBy(arg):
                name = arg.__name__
                if not name:
                    raise ValueError("Field has no name")
                fields.append((name, arg, arg.interface))

            elif self.managerInterface.providedBy(arg):
                for form_field in arg.values():
                    fields.append(
                        (form_field.__name__, form_field, form_field.interface))

            elif isinstance(arg, Field):
                fields.append((arg.__name__, arg, arg.interface))

            else:
                raise TypeError("Unrecognized argument type", arg)

        self._data_keys = []
        self._data_values = []
        self._data = {}

        for name, field, iface in fields:
            if isinstance(field, Field):
                form_field = field
            else:
                if field.readonly:
                    if omitReadOnly and (name not in keepReadOnly):
                        continue
                customDefaults = defaults.copy()
                if iface is not None:
                    customDefaults['interface'] = iface
                form_field = Field(field, **customDefaults)
                name = form_field.__name__

            if name in self._data:
                raise ValueError("Duplicate name", name)

            self._data_values.append(form_field)
            self._data_keys.append(name)
            self._data[name] = form_field

    def select(self, *names, **kwargs):
        """See interfaces.IFields"""
        prefix = kwargs.pop('prefix', None)
        interface = kwargs.pop('interface', None)
        assert len(kwargs) == 0
        if prefix:
            names = [util.expandPrefix(prefix) + name for name in names]
        mapping = self
        if interface is not None:
            mapping = dict([(field.field.__name__, field)
                            for field in self.values()
                            if field.field.interface is interface])
        return self.__class__(*[mapping[name] for name in names])

    def omit(self, *names, **kwargs):
        """See interfaces.IFields"""
        prefix = kwargs.pop('prefix', None)
        interface = kwargs.pop('interface', None)
        assert len(kwargs) == 0
        if prefix:
            names = [util.expandPrefix(prefix) + name for name in names]
        return self.__class__(
            *[field for name, field in self.items()
              if not ((name in names and interface is None) or
                      (field.field.interface is interface and
                       field.field.__name__ in names)) ])


class FieldWidgets(util.Manager):
    """Widget manager for IWidget."""
    config.adapts(
        interfaces.IFieldsForm, interface.Interface)
    interface.implementsOnly(interfaces.IWidgets)

    prefix = 'widgets.'
    mode = interfaces.INPUT_MODE
    errors = ()
    hasRequiredFields = False
    ignoreReadonly = False
    setErrors = True

    def __init__(self, form, request):
        super(FieldWidgets, self).__init__()
        self.form = form
        self.request = request

    def update(self):
        content = self.content = self.form.getContent()

        self._data = {}
        self._data_values = []

        # Create a unique prefix.
        prefix = util.expandPrefix(self.form.prefix)
        prefix += util.expandPrefix(self.prefix)
        request = self.request
        params = self.form.getRequestParams()
        context = self.form.getContext()

        sm = getSiteManager()

        # Walk through each field, making a widget out of it.
        uniqueOrderedKeys = []
        for field in self.form.fields.values():
            # Step 1: Determine the mode of the widget.
            mode = self.mode
            if field.mode is not None:
                mode = field.mode
            elif field.field.readonly and not self.ignoreReadonly:
                mode = interfaces.DISPLAY_MODE

            # Step 2: Get the widget for the given field.
            shortName = field.__name__

            widget = None
            factory = field.widgetFactory
            if isinstance(factory, basestring):
                widget = sm.queryMultiAdapter(
                    (field.field, request), interfaces.IWidget, name=factory)
            elif callable(factory):
                widget = factory(field.field, request)

            if widget is None:
                widget = sm.getMultiAdapter(
                    (field.field, request), interfaces.IDefaultWidget)

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

            # Step 7: Set the mode of the widget
            widget.mode = mode

            # Step 8: Update the widget
            widget.update()
            #zope.event.notify(AfterWidgetUpdateEvent(widget))

            # Step 9: Add the widget to the manager
            if widget.required:
                self.hasRequiredFields = True
            uniqueOrderedKeys.append(shortName)

            self._data_values.append(widget)
            self._data[shortName] = widget
            widget.__parent__ = self
            widget.__name__ = shortName

            # allways ensure that we add all keys and keep the order given from
            # button items
            self._data_keys = uniqueOrderedKeys

    def extract(self):
        """See interfaces.IWidgets"""
        data = {}
        sm = getSiteManager()
        errors = Errors()
        errorViews = []
        context = self.form.getContext()

        for name, widget in self.items():
            if widget.mode == interfaces.DISPLAY_MODE:
                continue

            value = widget.field.missing_value
            try:
                widget.setErrors = self.setErrors
                raw = widget.extract()
                if raw is not interfaces.NO_VALUE:
                    value = sm.getMultiAdapter(
                        (widget.field, widget), 
                        interfaces.IDataConverter).toFieldValue(raw)

                if value is interfaces.NOT_CHANGED:
                    value = sm.getMultiAdapter(
                        (self.context, field), interfaces.IDataManager).query()

                # validate value
                field = getattr(widget, 'field', None)
                if field is not None:
                    if context is not None:
                        field = field.bind(context)

                    if value is not interfaces.NOT_CHANGED:
                        field.validate(value)

            except (interface.Invalid, ValueError, MultipleErrors), error:
                errors.append(WidgetError(name, error))

            data[widget.__name__] = value

        # call form validation
        self.form.validate(data, errors)

        # prepare errors for viewing
        for error in errors:
            if interfaces.IWidgetError.providedBy(error):
                widget = self.get(error.name)
                error = error.error
            else:
                widget = None

            view = sm.queryMultiAdapter(
                (error, self.request), interfaces.IErrorViewSnippet)
            if view is None:
                view = ErrorViewSnippet(error, self.request)
            view.update(widget)
            errorViews.append(view)
            
            if self.setErrors and widget is not None:
                widget.error = view

        if self.setErrors:
            self.errors = errorViews

        return data, errorViews
