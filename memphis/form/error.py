"""Error views implementation"""
from memphis import config, view
from memphis.form.interfaces import _


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


class Invalid(Exception):

    def __init__(self, field, message):
        self.field = field
        self.message = message
