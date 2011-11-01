""" cms events """
import ptah
from ptah import config
from datetime import datetime
from zope.interface.interfaces import ObjectEvent


class ContentEvent(ObjectEvent):
    """ Base content event """

    object = None


class ContentCreatedEvent(ContentEvent):
    """ Event thrown by
        :py:class:`ptah.cms.TypeInformation` """
    config.event('Content created event')


class ContentAddedEvent(ContentEvent):
    """ Unused event.  To be removed """
    config.event('Content added event')


class ContentMovedEvent(ContentEvent):
    """ :py:class:`ptah.cms.Container` will
        notify when content has moved."""
    config.event('Content moved event')


class ContentModifiedEvent(ContentEvent):
    """ :py:class:`ptah.cms.Content` will
        notify when update() method invoked. """
    config.event('Content modified event')


class ContentDeletingEvent(ContentEvent):
    """ :py:class:`ptah.cms.Container` will
        notify when content deleted """
    config.event('Content deleting event')


@config.subscriber(ContentCreatedEvent)
def content_created_handler(ev):
    """ Assigns created, modified, __owner__
        attributes for newly created content """
    now = datetime.utcnow()
    ev.object.created = now
    ev.object.modified = now

    user = ptah.authService.get_userid()
    if user:
        ev.object.__owner__ = user


@config.subscriber(ContentModifiedEvent)
def content_modified_handler(ev):
    """ Updates the modified attribute on content """
    ev.object.modified = datetime.utcnow()
