"""Form implementation"""
from zope import interface
from collections import OrderedDict
from pyramid import security
from pyramid.i18n import get_localizer
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPForbidden
from webob.multidict import UnicodeMultiDict, MultiDict

from memphis import view, config
from memphis.form.field import Fieldset
from memphis.form.button import Buttons, Actions
from memphis.form.pagelets import FORM_VIEW
from memphis.form.interfaces import _, Invalid, FORM_INPUT, FORM_DISPLAY
from memphis.form.interfaces import IForm, IInputForm, IDisplayForm, IWidgets

CSRF = None

def setCsrfUtility(util):
    global CSRF
    CSRF = util


class FormErrorMessage(view.Message):
    config.adapter(None, name='form-error')

    formErrorsMessage = _(u'Please fix indicated errors.')

    template = view.template('memphis.form:templates/form-error.pt')

    def render(self, message):
        self.errors = [
            err for err in message
            if not isinstance(err, Invalid) or err.field is None]

        return self.template(
            message = self.formErrorsMessage,
            errors = self.errors,
            request = self.request)


class FormWidgets(OrderedDict):

    prefix = 'widgets.'
    fieldsets = ()

    def __init__(self, fields, form, request):
        super(FormWidgets, self).__init__()

        self.fields = fields
        self.form = form
        self.request = request
        self.localizer = get_localizer(request)

    def update(self):
        # Create a unique prefix.
        prefix = '%s%s'%(self.form.prefix, self.prefix)

        request = self.request
        params = self.form.getParams()
        content = self.form.getContent()
        self.fieldset = fieldset = self.fields.bind(content, params)
        self.fieldsets = fieldsets = []

        # Walk through each field, making a widget out of it.
        for fieldset in self.fieldset.fieldsets():
            widgets = []

            for widget in fieldset.fields():
                widget.localizer = self.localizer
                widget.id = ('%s%s'%(prefix, widget.name)).replace('.', '-')
                widget.__name__ = widget.name
                widget.__parent__ = self
                widget.update(request)
                widgets.append(widget)
                self[widget.name] = widget

            fieldsets.append(
                {'fieldset': fieldset,
                 'name': fieldset.name,
                 'legend': fieldset.legend,
                 'widgets': widgets})

    def extract(self, setErrors=True):
        data = {}
        errors = []

        data, errors = self.fieldset.extract()

        # form validation
        self.form.validate(data, errors)

        # set errors
        for error in errors:
            if setErrors and error.field is not None \
                   and error.field.error is None:
                error.field.error = error

        return data, errors


class Form(view.View):
    """A base form."""
    interface.implements(IForm, IInputForm)

    fields = Fieldset()
    buttons = Buttons()

    label = None
    description = ''

    prefix = 'form.'

    actions = None
    widgets  = None
    content = None

    mode = FORM_INPUT

    method = 'post'
    enctype = 'multipart/form-data'
    accept = None
    acceptCharset = None

    csrf = False
    csrfname = 'csrf-token'

    @property
    def action(self):
        return self.request.url

    @property
    def name(self):
        return self.prefix.strip('.')

    @property
    def id(self):
        return self.name.replace('.', '-')

    def getContent(self):
        return self.content

    def getParams(self):
        if self.method == 'post':
            return self.request.POST
        elif self.method == 'get':
            return self.request.GET
        else:
            return {}

    def updateWidgets(self):
        self.widgets = FormWidgets(self.fields, self, self.request)
        self.widgets.mode = self.mode
        self.widgets.update()

    def updateActions(self):
        self.actions = Actions(self, self.request)
        self.actions.update()

    @property
    def token(self):
        if CSRF is not None:
            return CSRF.generate(self.tokenData)

    @reify
    def tokenData(self):
        return '%s.%s:%s'%(self.__module__,self.__class__.__name__,
                           security.authenticated_userid(self.request))

    def validate(self, data, errors):
        self.validateToken()

    def validateToken(self):
        # check csrf token
        if self.csrf:
            token = self.getParams().get(self.csrfname, None)
            if token is not None:
                if CSRF is not None:
                    if CSRF.get(token) == self.tokenData:
                        return

            raise HTTPForbidden("Form authenticator is not found.")

    def extract(self, setErrors=True):
        return self.widgets.extract(setErrors)

    def update(self):
        self.updateWidgets()
        self.updateActions()

        self.actions.execute()

    def render(self):
        if self.template is None:
            return self.pagelet(FORM_VIEW, self)

        kwargs = {'view': self,
                  'context': self.context,
                  'request': self.request}

        return self.template(**kwargs)


class DisplayForm(Form):
    interface.implements(IDisplayForm)

    mode = FORM_DISPLAY
    empty = UnicodeMultiDict(MultiDict({}), 'utf-8')

    def getParams(self):
        return self.empty
