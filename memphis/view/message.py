""" status message implementation """
import cgi
from zope import interface
from zope.component import getAdapter, queryUtility
from pyramid.i18n import get_localizer
from pyramid.interfaces import IRequest

from memphis import config
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
        message = getAdapter(self.request, IMessage, type)

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

    def __init__(self, request):
        self.request = request


class InformationMessage(Message):
    config.adapts(IRequest, 'info')

    cssClass = 'statusMessage'

    def render(self, message):
        translate = get_localizer(self.request).translate

        return '<div class="%s">%s</div>'%(
            self.cssClass, cgi.escape(translate(message, self.request), True))


class WarningMessage(InformationMessage):
    config.adapts(IRequest, 'warning')

    cssClass = 'statusWarningMessage'


class ErrorMessage(InformationMessage):
    config.adapts(IRequest, 'error')

    cssClass = 'statusStopMessage'

    def render(self, e):
        if isinstance(e, Exception):
            message = '%s: %s'%(e.__class__.__name__, cgi.escape(str(e), True))
        else:
            message = e

        return super(ErrorMessage, self).render(message)
