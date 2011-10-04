from collections import OrderedDict
from pyramid.i18n import get_localizer

from memphis import config
from memphis.form.error import Invalid
from memphis.form.interfaces import FORM_INPUT, FORM_DISPLAY
from memphis.form.interfaces import \
    IForm, IField, IWidget, IWidgets, IDataManager


class Widgets(OrderedDict):

    prefix = 'widgets.'
    mode = FORM_INPUT
    errors = ()
    content = None
    fieldsets = ()

    def __init__(self, fields, form, request):
        super(Widgets, self).__init__()

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
        request = self.request
        self.params = params = self.form.getParams()

        self.fieldsets = fieldsets = []

        # Walk through each field, making a widget out of it.
        for fieldset in self.fields.fieldsets():
            widgets = []

            print fieldset

            if content is not None:
                wcontent = content.dataset(fieldset.name)
            else:
                wcontent = None

            for field in fieldset.fields():
                # Step 1: Get the widget for the given field.
                widget = field.bind(
                    wcontent, params, request,
                    localizer=self.localizer)

                # Step 2: Set the prefix for the widget
                name = '%s%s'%(fieldset.prefix, field.name)

                widget.id = ('%s%s'%(prefix, name)).replace('.', '-')
                widget.name = name
                widget.fieldset = fieldset.name
                widget.fieldname = field.name

                # Step 6: Set the mode of the widget
                #if field.mode is not None:
                #    widget.mode = field.mode
                #elif field.readonly:
                #    widget.mode = FORM_DISPLAY
                #else:
                #    widget.mode = self.mode

                # Step 9: Add the widget to the manager
                widget.__name__ = name
                widget.__parent__ = self
                widgets.append(widget)
                self[name] = widget

            fieldsets.append(
                {'name': fieldset.name,
                 'legend': fieldset.legend,
                 'widgets': widgets})

    def extract(self, setErrors=True):
        data = {}
        errors = []

        for name, widget in self.items():
            if widget.mode == FORM_DISPLAY:
                continue

            value = widget.missing
            try:
                value = widget.deserialize(widget.extract(self.params))
            except Invalid, error:
                errors.append(error)
                if setErrors:
                    widget.error = error

            data[widget.__name__] = value

        data = self.fields.unflatten(data)

        # validate against schemas
        extra_errors = []
        try:
            self.fields.validator(None, data)
        except Invalid, error:
            extra_errors.extend(error.children)

        # form validation
        self.form.validate(data, extra_errors)

        # prepare errors
        for error in extra_errors:
            errors.append(err)

            #if setErrors and widget is not None:
            #    widget.error = err

        self.errors = errors
        return data, errors
