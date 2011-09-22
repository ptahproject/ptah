""" ptah settings """
import colander
from memphis import config

PTAH_CONFIG = config.registerSettings(
    'ptah',

    config.SchemaNode(
        config.Sequence(), colander.SchemaNode(colander.Str()),
        name = 'managers',
        title = 'Managers',
        description = 'List of user logins with access rights to '\
            'ptah management ui.',
        default = ()),

    config.SchemaNode(
        colander.Str(),
        name = 'login',
        title = 'Login url',
        default = ''),

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

    title = 'Ptah settings',
    )
