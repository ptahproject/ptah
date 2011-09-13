import colander
from memphis import config, view

view.registerLayout(
    'ptah-security', parent='.',
    template = view.template('ptah.security:templates/layout.pt'))


AUTH_SETTINGS = config.registerSettings(
    'ptah-auth',

    config.SchemaNode(
        colander.Bool(),
        name = 'registration',
        title = 'Site registration',
        description = 'Enable/Disable site registration',
        default = True),

    config.SchemaNode(
        colander.Bool(),
        name = 'password',
        title = 'User password',
        description = 'Allow use to select password during registration',
        default = False),

    config.SchemaNode(
        colander.Bool(),
        name = 'validation',
        title = 'Email validation',
        description = 'Validate user account by email.',
        default = True),

    config.SchemaNode(
        colander.Bool(),
        name = 'allow-unvalidated',
        title = 'Allow un validation',
        description = 'Allow login for un Validated users.',
        default = True),

    config.SchemaNode(
        colander.Str(),
        name = 'pwdmanager',
        title = 'Password manager',
        description = 'Available password managers ("plain", "ssha", "bcrypt")',
        default = 'plain'),

    title = 'Ptah auth settings',
    )


class PrincipalEvent(object):
    """ base class for all principal related events """

    principal = None # IPrincipal object

    def __init__(self, principal):
        self.principal = principal


class LoggedInEvent(PrincipalEvent):
    """ User logged in to system."""
    config.event('Logged in event')


class LogingFailedEvent(PrincipalEvent):
    """ User loging failed."""
    config.event('Loging failed event')

    message = ''

    def __init__(self, principal, message=u''):
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


class PrincipalRegisteredEvent(PrincipalAddedEvent):
    """ Principal registered event """
