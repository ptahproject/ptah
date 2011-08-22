"""Form implementation"""
import sys
from zope import interface
from zope.component import getMultiAdapter

from webob.exc import HTTPFound
from webob.multidict import UnicodeMultiDict, MultiDict

from memphis import view, config
from memphis.form import button, field, interfaces, pagelets

_ = interfaces.MessageFactory

empty_params = UnicodeMultiDict(MultiDict({}), 'utf-8')


class Form(view.View):
    """A base form."""
    interface.implements(interfaces.IForm, interfaces.IInputForm)

    fields = field.Fields()
    buttons = button.Buttons()

    label = None
    description = ''

    prefix = 'form.'
    template = None

    actions = None
    widgets  = None

    content = None

    mode = interfaces.INPUT_MODE
    ignoreReadonly = False

    method = 'post'
    enctype = 'multipart/form-data'
    acceptCharset = None
    accept = None
    refreshActions = False

    @property
    def action(self):
        try:
            self.request.getURL()
        except:
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
        try:
            return self.request.params
        except:
            return UnicodeMultiDict(self.request.form, 'utf-8')

    def updateWidgets(self):
        self.widgets = getMultiAdapter(
            (self, self.request), interfaces.IWidgets)
        self.widgets.mode = self.mode
        self.widgets.ignoreReadonly = self.ignoreReadonly
        self.widgets.update()

    def updateActions(self):
        self.actions = button.Actions(self, self.request)
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
        # render content template
        if self.template is None:
            return view.renderPagelet(pagelets.IFormView, self, self.request)

        kwargs = {'view': self,
                  'context': self.context,
                  'request': self.request}

        return self.template(**kwargs)


class DisplayForm(Form):
    interface.implements(interfaces.IDisplayForm)

    mode = interfaces.DISPLAY_MODE

    def getRequestParams(self):
        return empty_params
