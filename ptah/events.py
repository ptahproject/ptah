from ptah import config

# config events

class AppStarting(object):
    """ ptah sends this event when application is ready to start. """
    config.event('Application starting event')

    config = None

    def __init__(self, config):
        self.config = config
        self.registry = config.registry


class Initialized(object):
    """ ptah sends this after ptah.config.initialize """
    config.event('Ptah config initialized event')

    def __init__(self, config):
        self.config = config


# settings related events

class SettingsInitializing(object):
    """ Settings initializing event """
    config.event('Settings initializing event')

    config = None
    registry = None

    def __init__(self, config, registry):
        self.config = config
        self.registry = registry


class SettingsInitialized(object):
    """ ptah sends this event when settings initialization is completed. """
    config.event('Settings initialized event')

    config = None
    registry = None

    def __init__(self, config, registry):
        self.config = config
        self.registry = registry


class SettingsGroupModified(object):
    """ ptah sends this event when settings group is modified. """
    config.event('Settings group modified event')

    def __init__(self, group):
        self.object = group


# principal events

class PrincipalEvent(object):
    """ base class for all principal related events """

    principal = None  # IPrincipal object

    def __init__(self, principal):  # pragma: no cover
        self.principal = principal


class LoggedInEvent(PrincipalEvent):
    """ User logged in to system."""
    config.event('Logged in event')


class LoginFailedEvent(PrincipalEvent):
    """ User login failed."""
    config.event('Login failed event')

    message = ''

    def __init__(self, principal, message=''):  # pragma: no cover
        self.principal = principal
        self.message = message


class LoggedOutEvent(PrincipalEvent):
    """ User logged out."""
    config.event('Logged out event')


class ResetPasswordInitiatedEvent(PrincipalEvent):
    """ User has initiated password changeing."""
    config.event('Reset password initiated event')


class PrincipalPasswordChangedEvent(PrincipalEvent):
    """ User password has been changed. """
    config.event('User password has been changed')


class PrincipalValidatedEvent(PrincipalEvent):
    """ Principal account has been validated."""
    config.event('Account validation event')


class PrincipalAddedEvent(PrincipalEvent):
    """ Principal added event """


class PrincipalRegisteredEvent(PrincipalEvent):
    """ Principal registered event """
