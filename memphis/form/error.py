"""Error views implementation"""
from zope import interface
from memphis import config, view
from memphis.form.interfaces import _, IError, IWidgetError


class FormErrorMessage(view.Message):
    config.adapter(None, name='form-error')

    formErrorsMessage = _(u'Please fix indicated errors.')

    template = view.template('memphis.form:templates/form-error.pt')

    def render(self, message):
        self.errors = [
            err for err in message
            if not IWidgetError.providedBy(err) or err.widget.error is None]

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
