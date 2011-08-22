"""Error views implementation"""
from zope import interface
from memphis import config, view
from memphis.form.interfaces import _, IError, IWidgetError


class FormErrorMessage(view.Message):
    config.adapts(None, name='form-error')

    template = view.template('memphis.form:templates/form-error.pt')

    formErrorsMessage = _(u'Please fix indicated errors.')

    def render(self, message):
        self.errors = [err for err in message 
                       if not IWidgetError.providedBy(err)]

        return self.template(
            message = self.formErrorsMessage,
            errors = self.errors,
            request = self.request)


class Error(object):
    interface.implements(IError)

    def __init__(self, error, message):
        self.error = error
        self.message = message


class WidgetError(Error):
    interface.implements(IWidgetError)

    def __init__(self, error, message, widget):
        self.error = error
        self.message = message
        self.widget = widget
