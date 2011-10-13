""" cms events """
import ptah
from memphis import config
from datetime import datetime
from zope.interface.interfaces import ObjectEvent


class ContentEvent(ObjectEvent):
    """ Base content event """

    object = None


class ContentCreatedEvent(ContentEvent):
    """ Event thrown by
        :py:class:`ptah_cms.TypeInformation` """
    config.event('Content created event')


class ContentAddedEvent(ContentEvent):
    """ Unused event.  To be removed """
    config.event('Content added event')


class ContentMovedEvent(ContentEvent):
    """ :py:class:`ptah_cms.Container` will
        notify when content has moved."""
    config.event('Content moved event')


class ContentModifiedEvent(ContentEvent):
    """ :py:class:`ptah_cms.Content` will
        notify when update() method invoked. """
    config.event('Content modified event')


class ContentDeletingEvent(ContentEvent):
    """ :py:class:`ptah_cms.Container` will
        notify when content deleted """
    config.event('Content deleting event')


@config.subscriber(ContentCreatedEvent)
def createdHandler(ev):
    """ Assigns created, modified, __owner__
        attributes for newly created content """
    now = datetime.utcnow()
    ev.object.created = now
    ev.object.modified = now

    user = ptah.authService.getUserId()
    if user:
        ev.object.__owner__ = user


@config.subscriber(ContentModifiedEvent)
def modifiedHandler(ev):
    """ Updates the modified attribute on content """
    ev.object.modified = datetime.utcnow()
