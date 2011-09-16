""" cms events """
import ptah
from memphis import config
from datetime import datetime
from zope.component.interfaces import ObjectEvent


class ContentEvent(ObjectEvent):

    object = None


class ContentCreatedEvent(ContentEvent):
    pass


class ContentAddedEvent(ContentEvent):
    pass


class ContentMovedEvent(ContentEvent):
    pass


class ContentModifiedEvent(ContentEvent):
    pass


class ContentDeletingEvent(ContentEvent):
    pass


@config.handler(ContentCreatedEvent)
def createdHandler(ev):
    now = datetime.now()
    ev.object.created = now
    ev.object.modified = now

    user = ptah.security.authService.getCurrentPrincipal()
    if user:
        ev.object.__owners__ = [user.uuid]


@config.handler(ContentModifiedEvent)
def modifiedHandler(ev):
    ev.object.modified = datetime.now()
