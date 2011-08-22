"""Error Views Implementation"""
import os
import colander
from zope import interface
from memphis import config, view
from memphis.form import interfaces, pagelets
from memphis.form.interfaces import _, IErrorViewSnippet
from memphis.form.interfaces import IErrors, IWidgetError


class FormErrorMessage(view.Message):
    config.adapts(None, name='form-error')

    template = view.template('memphis.form:templates/form-error.pt')

    formErrorsMessage = _(u'Please fix indicated errors.')

    def render(self, message):
        self.errors = [
            err for err in message
            if IErrorViewSnippet.providedBy(err) and err.widget is None]

        return self.template(
            message = self.formErrorsMessage,
            errors = self.errors,
            request = self.request)


class Errors(list):
    interface.implements(IErrors)
    
    def __init__(self, *args):
        super(Errors, self).__init__(*args)

        self.widgetErrors = {}

    def append(self, error):
        if IWidgetError.providedBy(error):
            self.widgetErrors[error.name] = error

        super(Errors, self).append(error)

    def extend(self, lst):
        for error in lst:
            self.append(error)

    def getWidgetError(self, name, default=None):
        return self.widgetErrors.get(name, default)


class WidgetError(object):
    interface.implements(IWidgetError)

    def __init__(self, name, error):
        self.name = name
        self.error = error


class ErrorViewSnippet(object):
    """Error view snippet."""
    interface.implements(IErrorViewSnippet)

    def __init__(self, error, request):
        self.error = self.context = error
        self.request = request

    def createMessage(self):
        return self.error

    def update(self, widget=None):
        self.widget = widget
        self.message = self.createMessage()

    def __repr__(self):
        return '<%s for %s>' %(self.__class__.__name__, self.error)


class ValueErrorViewSnippet(ErrorViewSnippet):
    """An error view for ValueError."""
    config.adapts(ValueError, None)

    defaultMessage = _('The system could not process the given value.')

    def createMessage(self):
        return self.defaultMessage


class InvalidErrorViewSnippet(ErrorViewSnippet):
    """Error view snippet."""
    config.adapts(colander.Invalid, None)

    def createMessage(self):
        return self.error.msg
