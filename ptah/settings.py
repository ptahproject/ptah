""" ptah settings """
import colander
from memphis import config

PTAH_CONFIG = config.register_settings(
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
        colander.Str(),
        name = 'pwdmanager',
        title = 'Password manager',
        description = 'Available password managers ("plain", "ssha", "bcrypt")',
        default = 'plain'),

    title = 'Ptah settings',
    )
