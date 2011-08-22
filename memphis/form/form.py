"""Form implementation"""
from zope import interface
from zope.component import getMultiAdapter
from webob.multidict import UnicodeMultiDict, MultiDict

from memphis import view
from memphis.form.field import Fields
from memphis.form.button import Buttons, Actions
from memphis.form.pagelets import IFormView
from memphis.form.interfaces import INPUT_MODE, DISPLAY_MODE
from memphis.form.interfaces import IForm, IInputForm, IDisplayForm, IWidgets


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

    mode = INPUT_MODE

    method = 'post'
    enctype = 'multipart/form-data'
    acceptCharset = None
    accept = None
    refreshActions = False

    @property
    def action(self):
        return self.request.url

    @property
    def name(self):
        return self.prefix.strip('.')

    @property
    def id(self):
        return self.name.replace('.', '-')

    def getContext(self):
        return self.context

    def getContent(self):
        return self.content

    def getRequestParams(self):
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

    def validate(self, data, errors):
        pass

    def extractData(self, setErrors=True):
        self.widgets.setErrors = setErrors
        return self.widgets.extract()

    def update(self):
        self.updateWidgets()
        self.updateActions()

        self.actions.execute()
        if self.refreshActions:
            self.updateActions()

    def render(self):
        if self.template is None:
            return self.pagelet(IFormView, self)

        kwargs = {'view': self,
                  'context': self.context,
                  'request': self.request}

        return self.template(**kwargs)


class DisplayForm(Form):
    interface.implements(IDisplayForm)

    mode = DISPLAY_MODE
    empty = UnicodeMultiDict(MultiDict({}), 'utf-8')

    def getRequestParams(self):
        return self.empty
