""" status message implementation """
import cgi
from zope.interface import implementer
from pyramid.interfaces import IRequest
from pyramid.compat import binary_type

import ptah
from ptah.view.tmpl import template as get_template
from ptah.view.interfaces import IMessage, IStatusMessage


def add_message(request, msg, type='info'):
    srv = get_message_service(request)
    if srv is not None:
        srv.add(msg, type)


def get_message_service(request):
    return MessageService(request)


def render_messages(request):
    service = get_message_service(request)
    messages = service.clear()
    if messages:
        return '\n'.join(messages)
    return ''


@implementer(IStatusMessage)
class MessageService(object):
    """ message service """

    SESSIONKEY = 'msgservice'

    def __init__(self, request):
        self.request = request
        try:
            self.session = request.session
        except:
            self.session = {}

    def add(self, text, type='info'):
        request = self.request

        message = request.registry.getAdapter(request, IMessage, type)

        messages = self.session.get(self.SESSIONKEY, [])

        text = message.render(text)
        if text not in self.messages():
            messages.append(text)
        self.session[self.SESSIONKEY] = messages

    def clear(self):
        messages = self.session.get(self.SESSIONKEY)
        if messages is not None:
            if messages:
                del self.session[self.SESSIONKEY]
                return messages
        return ()

    def messages(self):
        messages = self.session.get(self.SESSIONKEY)
        if messages is not None:
            return messages
        return ()


@implementer(IMessage)
class Message(object):
    """ Basic message """

    template = None

    def __init__(self, request):
        self.request = request

    def render(self, message):
        return self.template(message = message, request = self.request)


@ptah.adapter(IRequest, name='info')
class InformationMessage(Message):

    template = get_template('ptah.view:templates/msg-info.pt')


@ptah.adapter(IRequest, name='success')
class SuccessMessage(Message):

    template = get_template('ptah.view:templates/msg-success.pt')


@ptah.adapter(IRequest, name='warning')
class WarningMessage(Message):

    template = get_template('ptah.view:templates/msg-warning.pt')


@ptah.adapter(IRequest, name='error')
class ErrorMessage(Message):

    template = get_template('ptah.view:templates/msg-error.pt')

    def render(self, e):
        if isinstance(e, Exception):
            message = '%s: %s'%(e.__class__.__name__,
                                cgi.escape(str(e), True))
        else:
            message = e

        return super(ErrorMessage, self).render(message)
