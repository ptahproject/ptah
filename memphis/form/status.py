"""  formError status message type

$Id:  2007-12-12 12:27:02Z fafhrd $
"""
from zope import interface
from pyramid.interfaces import IRequest

from memphis import view, config
from memphis.view.message import Message
from memphis.form.interfaces import IErrorViewSnippet


class FormErrorStatusMessage(Message):
    config.adapts(IRequest, 'formError')

    template = view.template('memphis.form:templates/message.pt')

    def render(self, message):
        self.message = message[0]
        self.errors = [
            err for err in message[1:]
            if IErrorViewSnippet.providedBy(err) and err.widget is None]
        return self.template(view = self)
