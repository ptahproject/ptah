""" ptah settings """
import colander
from memphis import config


PTAH = config.registerSettings(
    'ptah',

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
        config.Sequence(), colander.SchemaNode(colander.Str()),
        name = 'managers',
        title = 'Managers',
        description = 'List of user logins with access rights to ptah management ui.',
        default = ()),

    title = 'Ptah settings',
    )
