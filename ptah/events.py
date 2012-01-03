from ptah import config
from zope.interface.interfaces import ObjectEvent


class event(object):
    """ Register event object, it is used for introspection only. """

    ID_EVENT = 'ptah.config:event'

    #: Event name
    name = ''

    #: Event title
    title = ''

    #: Event category
    category = ''

    #: Event class or interface
    factory = None

    def __init__(self, title='', category=''):
        self.title = title
        self.category = category

        self.info = config.DirectiveInfo()

    def __call__(self, cls):
        self.factory = cls
        self.description = cls.__doc__
        self.name = '{0}.{1}'.format(cls.__module__, cls.__name__)

        discr = (self.ID_EVENT, self.name)
        intr = config.Introspectable(
            self.ID_EVENT, discr, self.description, self.title)
        intr['ev'] = self
        intr['name'] = self.name
        intr['codeinfo'] = self.info.codeinfo

        def _event(cfg, desc, intr):
            storage = cfg.get_cfg_storage(self.ID_EVENT)
            storage[desc.name] = desc
            storage[desc.factory] = desc

        self.info.attach(
            config.Action(_event, (self, intr),
                          discriminator=discr, introspectables=(intr,))
            )
        return cls


# settings related events

@event('Settings initializing event')
class SettingsInitializing(object):
    """ Settings initializing event """

    config = None
    registry = None

    def __init__(self, config, registry):
        self.config = config
        self.registry = registry


@event('Settings initialized event')
class SettingsInitialized(object):
    """ ptah sends this event when settings initialization is completed. """

    config = None
    registry = None

    def __init__(self, config, registry):
        self.config = config
        self.registry = registry


@event('Settings group modified event')
class SettingsGroupModified(object):
    """ ptah sends this event when settings group is modified. """

    def __init__(self, group):
        self.object = group


# uri events

@event('Uri invalidate event')
class UriInvalidateEvent(object):
    """ Uri object has been changed. """

    def __init__(self, uri):
        self.uri = uri


# principal events

class PrincipalEvent(object):
    """ base class for all principal related events """

    principal = None  # IPrincipal object

    def __init__(self, principal):  # pragma: no cover
        self.principal = principal


@event('Logged in event')
class LoggedInEvent(PrincipalEvent):
    """ User logged in to system."""


@event('Login failed event')
class LoginFailedEvent(PrincipalEvent):
    """ User login failed."""

    message = ''

    def __init__(self, principal, message=''):  # pragma: no cover
        self.principal = principal
        self.message = message


@event('Logged out event')
class LoggedOutEvent(PrincipalEvent):
    """ User logged out."""


@event('Reset password initiated event')
class ResetPasswordInitiatedEvent(PrincipalEvent):
    """ User has initiated password changeing."""


@event('User password has been changed')
class PrincipalPasswordChangedEvent(PrincipalEvent):
    """ User password has been changed. """


@event('Account validation event')
class PrincipalValidatedEvent(PrincipalEvent):
    """ Principal account has been validated."""


@event('Principal added event')
class PrincipalAddedEvent(PrincipalEvent):
    """ Principal added event """


@event('Principal registered event')
class PrincipalRegisteredEvent(PrincipalEvent):
    """ Principal registered event """


# content events

class ContentEvent(ObjectEvent):
    """ Base content event """

    object = None


@event('Content created event')
class ContentCreatedEvent(ContentEvent):
    """ :py:class:`ptah.cms.TypeInformation` will send event during create().
    """


@event('Content added event')
class ContentAddedEvent(ContentEvent):
    """ :py:class:`ptah.cms.Container` will send event when content has been
        created through containers __setitem__ method.
    """


@event('Content moved event')
class ContentMovedEvent(ContentEvent):
    """ :py:class:`ptah.cms.Container` will send event when content has moved.
    """


@event('Content modified event')
class ContentModifiedEvent(ContentEvent):
    """ :py:class:`ptah.cms.Content` will send event during update().
    """


@event('Content deleting event')
class ContentDeletingEvent(ContentEvent):
    """ :py:class:`ptah.cms.Container` will send event before content has been
        deleted through containers __delitem__ method.
    """


# db schema creation
class BeforeCreateDbSchema(object):
    """ :py:data:`ptah.POPULATE_DB_SCHEMA` populate step sends event before
    tables have been created.

    ``registry``: Pyramid registry object
    """

    def __init__(self, registry):
        self.registry = registry
