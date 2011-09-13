"""Form implementation"""
from zope import interface
from zope.component import queryUtility, getMultiAdapter
from pyramid import security
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPForbidden
from webob.multidict import UnicodeMultiDict, MultiDict

from memphis import view
from memphis.form.field import Fields
from memphis.form.button import Buttons, Actions
from memphis.form.pagelets import FORM_VIEW, FORM_INPUT, FORM_DISPLAY
from memphis.form.interfaces import \
    IForm, IInputForm, IDisplayForm, IWidgets, ICSRFService


class Form(view.View):
    """A base form."""
    interface.implements(IForm, IInputForm)

    fields = Fields()
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
        self.widgets = getMultiAdapter((self, self.request), IWidgets)
        self.widgets.mode = self.mode
        self.widgets.update()

    def updateActions(self):
        self.actions = Actions(self, self.request)
        self.actions.update()

    @property
    def token(self):
        srv = queryUtility(ICSRFService)
        if srv is not None:
            return srv.generate(self.tokenData)

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
                srv = queryUtility(ICSRFService)
                if srv is not None:
                    if srv.get(token) == self.tokenData:
                        return

            raise HTTPForbidden("Form authenticator is not found.")

    def extractData(self, setErrors=True):
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
