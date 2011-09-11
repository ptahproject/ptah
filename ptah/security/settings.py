""" crowd settings """
import colander
from memphis import config


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
        default = False),

    config.SchemaNode(
        colander.Str(),
        name = 'pwdmanager',
        title = 'Password manager',
        description = 'Available password managers ("plain", "ssha", "bcrypt")',
        default = 'plain'),

    title = 'Ptah auth settings',
    )
