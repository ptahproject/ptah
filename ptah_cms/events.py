""" cms events """
import ptah
from memphis import config
from datetime import datetime
from zope.interface.interfaces import ObjectEvent


class ContentEvent(ObjectEvent):

    object = None


class ContentCreatedEvent(ContentEvent):
    """ """


class ContentAddedEvent(ContentEvent):
    """ """


class ContentMovedEvent(ContentEvent):
    """ """


class ContentModifiedEvent(ContentEvent):
    """ """


class ContentDeletingEvent(ContentEvent):
    """ """


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
