import colander
import translationstring
from ptah import config, view

_ = translationstring.TranslationStringFactory('ptah.crowd')


CROWD = config.register_settings(
    'ptah-crowd',

    config.SchemaNode(
        colander.Bool(),
        name = 'provider',
        title = 'Default user provider',
        description = 'Enable/Disable default provider',
        default = True),

    config.SchemaNode(
        colander.Bool(),
        name = 'join',
        title = 'Site registration',
        description = 'Enable/Disable site registration',
        default = True),

    config.SchemaNode(
        colander.Str(),
        name = 'joinurl',
        title = 'Join form url',
        default = ''),

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

    title = 'Ptah crowd settings',
    )
