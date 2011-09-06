""" crowd settings """
import colander
from memphis import config


CROWD = config.registerSettings(
    'ptah-crowd',

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

    title = 'Ptah crowd settings',
    )
