""" status message implementation """
import cgi
from zope import interface
from pyramid.interfaces import IRequest

from memphis import config
from memphis.view.tmpl import template as get_template
from memphis.view.interfaces import IMessage, IStatusMessage


def addMessage(request, msg, type='info'):
    srv = IStatusMessage(request, None)
    if srv is not None:
        srv.add(msg, type)


class MessageService(object):
    """ message service """
    interface.implements(IStatusMessage)

    SESSIONKEY = 'msgservice'

    def __init__(self, request):
        self.request = request
        try:
            self.session = request.session
        except:
            self.session = {}

    def add(self, text, type='info'):
        message = config.registry.getAdapter(self.request, IMessage, type)

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


class Message(object):
    interface.implements(IMessage)

    template = None

    def __init__(self, request):
        self.request = request

    def render(self, message):
        return self.template(message = message, request = self.request)


class InformationMessage(Message):
    config.adapter(IRequest, name='info')

    template = get_template('memphis.view:templates/msg-info.pt')


class SuccessMessage(Message):
    config.adapter(IRequest, name='success')

    template = get_template('memphis.view:templates/msg-success.pt')


class WarningMessage(Message):
    config.adapter(IRequest, name='warning')

    template = get_template('memphis.view:templates/msg-warning.pt')


class ErrorMessage(Message):
    config.adapter(IRequest, name='error')

    template = get_template('memphis.view:templates/msg-error.pt')

    def render(self, e):
        if isinstance(e, Exception):
            message = '%s: %s'%(e.__class__.__name__,
                                cgi.escape(str(e), True))
        else:
            message = e

        return super(ErrorMessage, self).render(message)


@config.adapter(IRequest)
@interface.implementer(IStatusMessage)
def getMessageService(request):
    service = config.registry.queryUtility(IStatusMessage)
    if service is None:
        service = MessageService(request)
    return service


def renderMessages(request):
    service = IStatusMessage(request, None)
    if service is not None:
        messages = service.clear()
        if messages:
            return u'\n'.join(messages)

    return u''
