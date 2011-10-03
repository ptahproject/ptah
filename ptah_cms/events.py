""" cms events """
import ptah
from memphis import config
from datetime import datetime
from zope.interface.interfaces import ObjectEvent


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


@config.subscriber(ContentCreatedEvent)
def createdHandler(ev):
    now = datetime.utcnow()
    ev.object.created = now
    ev.object.modified = now

    user = ptah.authService.getUserId()
    if user:
        ev.object.__owner__ = user


@config.subscriber(ContentModifiedEvent)
def modifiedHandler(ev):
    ev.object.modified = datetime.utcnow()
