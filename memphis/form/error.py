"""Error Views Implementation"""
import os
import colander
from zope import interface
from memphis import config, view
from memphis.form import interfaces, util, pagelets

_ = interfaces.MessageFactory


class Errors(list):
    interface.implements(interfaces.IErrors)
    
    def __init__(self, *args):
        super(Errors, self).__init__(*args)

        self.widgetErrors = {}

    def append(self, error):
        if interfaces.IWidgetError.providedBy(error):
            self.widgetErrors[error.name] = error

        super(Errors, self).append(error)

    def extend(self, lst):
        for error in lst:
            self.append(error)

    def getWidgetError(self, name, default=None):
        return self.widgetErrors.get(name, default)


class WidgetError(object):
    interface.implements(interfaces.IWidgetError)

    def __init__(self, name, error):
        self.name = name
        self.error = error


class ErrorViewSnippet(object):
    """Error view snippet."""
    interface.implements(interfaces.IErrorViewSnippet)

    def __init__(self, error, request):
        self.error = self.context = error
        self.request = request

    def createMessage(self):
        return self.error

    def update(self, widget=None):
        self.widget = widget
        self.message = self.createMessage()

    def render(self):
        return view.renderPagelet(
            pagelets.IErrorViewSnippetView, self, self.request)

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


class MultipleErrorViewSnippet(ErrorViewSnippet):
    """Error view snippet for multiple errors."""
    config.adapts(interfaces.IMultipleErrors, None)

    def update(self):
        pass

    def render(self):
        return u''.join(view.render() for view in self.error.errors)


class MultipleErrors(Exception):
    """An error that contains many errors"""
    interface.implements(interfaces.IMultipleErrors)

    def __init__(self, errors):
        self.errors = errors
