from ptah import config
from zope.interface.interfaces import ObjectEvent


# settings related events

@config.event('Settings initializing event')
class SettingsInitializing(object):
    """ Settings initializing event """

    config = None
    registry = None

    def __init__(self, config, registry):
        self.config = config
        self.registry = registry


@config.event('Settings initialized event')
class SettingsInitialized(object):
    """ ptah sends this event when settings initialization is completed. """

    config = None
    registry = None

    def __init__(self, config, registry):
        self.config = config
        self.registry = registry


@config.event('Settings group modified event')
class SettingsGroupModified(object):
    """ ptah sends this event when settings group is modified. """

    def __init__(self, group):
        self.object = group


# principal events

class PrincipalEvent(object):
    """ base class for all principal related events """

    principal = None  # IPrincipal object

    def __init__(self, principal):  # pragma: no cover
        self.principal = principal


@config.event('Logged in event')
class LoggedInEvent(PrincipalEvent):
    """ User logged in to system."""


@config.event('Login failed event')
class LoginFailedEvent(PrincipalEvent):
    """ User login failed."""

    message = ''

    def __init__(self, principal, message=''):  # pragma: no cover
        self.principal = principal
        self.message = message


@config.event('Logged out event')
class LoggedOutEvent(PrincipalEvent):
    """ User logged out."""


@config.event('Reset password initiated event')
class ResetPasswordInitiatedEvent(PrincipalEvent):
    """ User has initiated password changeing."""


@config.event('User password has been changed')
class PrincipalPasswordChangedEvent(PrincipalEvent):
    """ User password has been changed. """


@config.event('Account validation event')
class PrincipalValidatedEvent(PrincipalEvent):
    """ Principal account has been validated."""


@config.event('Principal added event')
class PrincipalAddedEvent(PrincipalEvent):
    """ Principal added event """


@config.event('Principal registered event')
class PrincipalRegisteredEvent(PrincipalEvent):
    """ Principal registered event """


# content events

class ContentEvent(ObjectEvent):
    """ Base content event """

    object = None


@config.event('Content created event')
class ContentCreatedEvent(ContentEvent):
    """ Event thrown by
        :py:class:`ptah.cms.TypeInformation` """


@config.event('Content added event')
class ContentAddedEvent(ContentEvent):
    """ Unused event.  To be removed """


@config.event('Content moved event')
class ContentMovedEvent(ContentEvent):
    """ :py:class:`ptah.cms.Container` will
        notify when content has moved."""


@config.event('Content modified event')
class ContentModifiedEvent(ContentEvent):
    """ :py:class:`ptah.cms.Content` will
        notify when update() method invoked. """


@config.event('Content deleting event')
class ContentDeletingEvent(ContentEvent):
    """ :py:class:`ptah.cms.Container` will
        notify when content deleted """
