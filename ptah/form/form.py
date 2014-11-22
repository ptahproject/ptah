"""Form implementation"""
from collections import OrderedDict
from webob.multidict import MultiDict
from pyramid.compat import string_types
from pyramid.decorator import reify
from pyramid.renderers import NullRendererHelper
from pyramid.interfaces import IResponse
from pyramid.httpexceptions import HTTPException, HTTPForbidden
from pyramid.config.views import DefaultViewMapper
from ptah.renderer import layout, render, tmpl_filter, add_message

from ptah.form.field import Field
from ptah.form.fieldset import Fieldset
from ptah.form.button import Buttons, Actions
from ptah.form.interfaces import Invalid, HTTPResponseIsReady


@tmpl_filter('form:error')
def form_error_message(context, request):
    """ form error renderer """
    errors = [err for err in context
              if (isinstance(err, str) or
                  (isinstance(err, Invalid) and err.field is None))]

    return {'errors': errors}


class FormWidgets(OrderedDict):
    """ Form widgets manager.
    Widget is bound to content field. """

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
        form = self.form
        params = form.form_params()
        content = form.form_content()
        prefix = '%s%s' % (form.prefix, self.prefix)
        fieldsets = self.fieldsets = []

        self.fieldset = self.form_fields.bind(
            self.request, content, params, prefix, form)

        # Walk through each field, making a widget out of it.
        for fieldset in self.fieldset.fieldsets():
            widgets = []

            for widget in fieldset.fields():
                widget.update()
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
        self.form.validate_form(data, errors)

        # convert strings
        errors = [Invalid(err) if isinstance(err, string_types) else err
                  for err in errors]

        # set errors to fields
        for err in errors:
            if isinstance(err.field, Field) and err.field.error is None:
                err.field.error = err

        return data, errors


class FormViewMapper(DefaultViewMapper):

    def __init__(self, **kw):
        super(FormViewMapper, self).__init__(**kw)

        renderer = kw.get('renderer')
        is_layout = isinstance(renderer, layout)

        if is_layout and not (renderer.name or renderer.renderer):
            self.map_class_native = self.map_class_native_layout

        elif is_layout and renderer.name:
            self.map_class_native = self.map_class_native_update

        elif not is_layout and not (renderer is None or
                  isinstance(renderer, NullRendererHelper)):
            self.map_class_native = self.map_class_native_update

    def map_class_native_layout(self, form_view):
        def _class_view(context, request, _view=form_view):
            inst = _view(context, request)
            request.__original_view__ = inst

            try:
                result = inst.update_form()
                if result is None:
                    result = {}
            except HTTPResponseIsReady as result:
                return result.args[0]
            except HTTPException as result:
                return result

            return inst.render()
        return _class_view

    def map_class_native_update(self, form_view):
        def _class_view(context, request, _view=form_view):
            inst = _view(context, request)
            request.__original_view__ = inst

            try:
                result = inst.update_form()
                if result is None:
                    result = {}
            except HTTPResponseIsReady as exc:
                result = exc.args[0]
            except HTTPException as exc:
                result = exc

            request.__view__ = inst
            return result
        return _class_view


class Form(object):
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

    ``params``: Form request parameters

    ``action``: Form action, by default ``request.url``

    ``method``: HTML Form method (`post`, `get`)

    ``csrf``: Enable/disable form csrf protection

    ``csrf_name``: Form csrf field name

    ``csrf_token``: Form csrf token value
    """

    label = None
    description = ''
    prefix = 'form.'

    actions = None
    widgets = None

    buttons = None
    fields = Fieldset()

    content = None

    method = 'post'
    enctype = 'multipart/form-data'
    accept = None
    accept_charset = 'utf-8'
    params = None
    context = None
    klass = 'form-horizontal'

    csrf = False
    csrf_name = 'csrf-token'
    csrf_token = ''

    tmpl_view = 'form:form'
    tmpl_actions = 'form:form-actions'
    tmpl_widget = 'form:widget'

    __name__ = ''
    __parent__ = None
    __view_mapper__ = FormViewMapper

    def __init__(self, context, request, **kw):
        self.__dict__.update(kw)

        self.context = context
        self.request = request
        self.__parent__ = context

        if self.buttons is None:
            self.buttons = Buttons()

        # convert fields to Fieldset
        if not isinstance(self.fields, Fieldset):
            self.fields = Fieldset(*self.fields)

        # set tmpl_widget
        for fieldset in self.fields.fieldsets():
            for field in fieldset.fields():
                if field.cls.tmpl_widget is None:
                    field.cls.tmpl_widget = self.tmpl_widget

    @reify
    def id(self):
        return self.name.replace('.', '-')

    @reify
    def name(self):
        return self.prefix.strip('.')

    @reify
    def action(self):
        return self.request.url

    @reify
    def csrf_token(self):
        return self.request.session.get_csrf_token()

    def form_content(self):
        """ Return form content.
        By default it returns ``Form.content`` attribute. """
        return self.content

    def form_params(self):
        """ get form request params """
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
        self.widgets.update()

    def update_actions(self):
        """ Prepare form actions, this method should be called directly.
        ``Form.update`` calls this method during initialization."""
        self.actions = Actions(self, self.request)
        self.actions.update()

    def update_form(self, data=None):
        """ update form """
        if not self.content and data:
            self.content = data

        self.update_widgets()
        self.update_actions()

        ac_result = self.actions.execute()
        if IResponse.providedBy(ac_result):
            raise HTTPResponseIsReady(ac_result)

        result = self.update()
        if IResponse.providedBy(result):
            raise HTTPResponseIsReady(result)

        if result is None:
            result = {}

        if ac_result is not None:
            result.update(ac_result)

        return result

    def update(self):
        """ Update form """
        return {}

    def render(self):
        """ render form """
        return render(self.request, self.tmpl_view, self,
                      actions = self.actions,
                      widgets = self.widgets)

    def validate(self, data, errors):
        """ Custom form validation """

    def validate_form(self, data, errors):
        """ Form validation """
        self.validate_csrf_token()
        try:
            self.validate(data, errors)
        except Invalid as err:
            errors.append(err)

    def validate_csrf_token(self):
        """ csrf token validation """
        if self.csrf:
            token = self.form_params().get(self.csrf_name, None)
            if token is not None:
                if self.csrf_token == token:
                    return

            raise HTTPForbidden("Form authenticator is not found.")

    def extract(self):
        """ extract form values """
        return self.widgets.extract()

    def add_error_message(self, msg):
        """ add form error message """
        add_message(self.request, msg, 'form:error')

    def __call__(self):
        """ update form and render form to response """
        try:
            result = self.update_form()
        except HTTPResponseIsReady as result:
            return result.args[0]
        except HTTPException as result:
            return result

        response = self.request.registry.queryAdapterOrSelf(result, IResponse)
        if response is not None:
            return response

        body = self.render()

        response = self.request.response
        if isinstance(body, bytes):
            response.body = body
        else:
            response.text = body
        return response
