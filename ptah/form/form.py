"""Form implementation"""
from collections import OrderedDict
from webob.multidict import MultiDict
from pyramid import security
from pyramid.decorator import reify
from pyramid.renderers import render, NullRendererHelper
from pyramid.interfaces import IResponse
from pyramid.httpexceptions import HTTPForbidden
from pyramid.config.views import DefaultViewMapper

import ptah
from ptah.view import Message
from ptah.form.field import Field, Fieldset
from ptah.form.button import Buttons, Actions
from ptah.form.interfaces import _, Invalid, FORM_INPUT, FORM_DISPLAY, IForm


@ptah.snippet('form-error', Message,
              renderer='ptah.form:templates/form-error.pt')
def formErrorMessage(context, request):
    """ form error renderer """
    errors = [err for err in context.message
              if isinstance(err, Invalid) and err.field is None]

    return {'errors': errors}


class FormWidgets(OrderedDict):
    """ Form widgets manager.
    Widget is bound to content field. """

    mode = FORM_INPUT
    prefix = 'widgets.'
    fieldsets = ()

    def __init__(self, fields, form, request):
        self.form_fields = fields
        self.form = form
        self.request = request

        super(FormWidgets, self).__init__()

    def fields(self):
        return self.fieldset.fields()

    def update(self):
        params = self.form.form_params()
        content = self.form.form_content()
        prefix = '%s%s' % (self.form.prefix, self.prefix)

        self.fieldset = self.form_fields.bind(content, params)
        self.fieldsets = fieldsets = []

        # Walk through each field, making a widget out of it.
        for fieldset in self.fieldset.fieldsets():
            widgets = []

            for widget in fieldset.fields():
                if widget.mode is None:
                    widget.mode = self.mode
                widget.id = ('%s%s' % (prefix, widget.name)).replace('.', '-')
                widget.update(self.request)
                widgets.append(widget)
                self[widget.name] = widget

            fieldsets.append(
                {'fieldset': fieldset,
                 'name': fieldset.name,
                 'title': fieldset.title,
                 'widgets': widgets})

    def extract(self):
        data, errors = self.fieldset.extract()

        # additional form validation
        self.form.validate(data, errors)

        # set errors to fields
        for err in errors:
            if isinstance(err.field, Field) and err.field.error is None:
                err.field.error = err

        return data, errors


class FormViewMapper(DefaultViewMapper):

    def __init__(self, **kw):
        super(FormViewMapper, self).__init__(**kw)

        renderer = kw.get('renderer')
        if not (renderer is None or isinstance(renderer, NullRendererHelper)):
            self.map_class_native = self.map_class_native_update

    def map_class_native_update(self, form_view):
        def _class_view(context, request, _view=form_view):
            inst = _view(context, request)
            request.__original_view__ = inst
            res = inst.render_update()
            request.__view__ = inst
            return res
        return _class_view


class Form(ptah.View):
    """ A form

    ``id``: Form id

    ``name``: Form name

    ``label``: Form label

    ``description``: Form description

    ``prefix``: Form prefix, it used for html elements `id` generations.

    ``fields``: Form fields :py:class:`ptah.form.Fieldset`

    ``buttons``: Form buttons :py:class:`ptah.form.Buttons`

    ``actions``: Instance of :py:class:`ptah.form.Actions` class

    ``widgets``: Instance of :py:class:`FormWidgets` class

    ``content``: Form content, it should be `None` or dictionary with
    data for fields.

    ``params``: None

    ``mode``: Form mode. It can be :py:data:`ptah.form.FORM_INPUT` or
        :py:data:`ptah.form.FORM_DISPLAY`

    ``action``: Form action, by default ``request.url``

    ``method``: HTML Form method (`post`, `get`)

    ``csrf``: Enable/disable form csrf protection

    ``token``: csrf token

    ``csrf-name``: csrf field name

    """

    fields = Fieldset()

    buttons = None

    label = None

    description = ''

    prefix = 'form.'

    actions = None

    widgets = None

    content = None

    mode = FORM_INPUT

    method = 'post'
    enctype = 'multipart/form-data'
    accept = None
    acceptCharset = None
    params = None

    csrf = False

    csrfname = 'csrf-token'

    __view_mapper__ = FormViewMapper

    def __init__(self, context, request):
        super(Form, self).__init__(context, request)

        if self.buttons is None:
            self.buttons = Buttons()

    @reify
    def action(self):
        return self.request.url

    @reify
    def name(self):
        return self.prefix.strip('.')

    @reify
    def id(self):
        return self.name.replace('.', '-')

    def form_content(self):
        """ Return form content.
        By default it returns ``Form.content`` attribute. """
        return self.content

    def form_params(self):
        """ get request params """
        if self.params is not None:
            if not isinstance(self.params, MultiDict):
                return MultiDict(self.params)
            return self.params

        if self.method == 'post':
            return self.request.POST
        elif self.method == 'get':
            return self.request.GET
        else:
            return self.params

    def update_widgets(self):
        """ prepare form widgets """
        self.widgets = FormWidgets(self.fields, self, self.request)
        self.widgets.mode = self.mode
        self.widgets.update()

    def update_actions(self):
        """ Prepare form actions, this method should be called directly.
        ``Form.update`` calls this method during initialization."""
        self.actions = Actions(self, self.request)
        self.actions.update()

    @property
    def token(self):
        return self.request.session.get_csrf_token()

    def validate(self, data, errors):
        """ additional form validation """
        self.validate_csrf_token()

    def validate_csrf_token(self):
        """ csrf token validation """
        if self.csrf:
            token = self.form_params().get(self.csrfname, None)
            if token is not None:
                if self.token == token:
                    return

            raise HTTPForbidden("Form authenticator is not found.")

    def extract(self):
        """ extract form values """
        return self.widgets.extract()

    def update(self, **data):
        """ update form """
        if not self.content and data:
            self.content = data

        self.update_widgets()
        self.update_actions()

        return self.actions.execute()

    def render(self):
        """ render form """
        return self.snippet(FORM_VIEW, self)

    def render_update(self):
        result = self.update()
        if result is None:
            result = {}

        return result

    def __call__(self):
        """ update form and render form to response """
        result = self.update()

        response = self.request.registry.queryAdapterOrSelf(result, IResponse)
        if response is not None:
            return response

        response = self.request.response
        body = self.render()
        if isinstance(body, bytes):
            response.body = body # pragma: no cover
        else:
            response.text = body
        return response


class DisplayForm(Form):
    """ Special form that just display content """

    mode = FORM_DISPLAY
    params = MultiDict([])

    def form_params(self):
        return self.params


FORM_VIEW = 'form-view'
FORM_ACTIONS = 'form-actions'
FORM_WIDGET = 'form-widget'
FORM_DISPLAY_WIDGET = 'form-display-widget'

ptah.snippet.register(
    FORM_VIEW, Form,
    renderer='ptah.form:templates/form.pt')

ptah.snippet.register(
    FORM_VIEW, DisplayForm,
    renderer='ptah.form:templates/form-display.pt')

ptah.snippet.register(
    FORM_ACTIONS, Form,
    renderer='ptah.form:templates/form-actions.pt')

ptah.snippet.register(
    FORM_WIDGET, Field,
    renderer='ptah.form:templates/widget.pt')

ptah.snippet.register(
    FORM_DISPLAY_WIDGET, Field,
    renderer='ptah.form:templates/widget-display.pt')
