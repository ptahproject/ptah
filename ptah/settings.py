""" ptah settings """
import colander
import translationstring
from ptah import config

_ = translationstring.TranslationStringFactory('ptah')


SECURITY = config.register_settings(
    'auth',

    config.SchemaNode(
        colander.Bool(),
        name = 'policy',
        title = _('Authentication policy'),
        description = _('Enable authentication policy.'),
        required = False,
        default = False),

    config.SchemaNode(
        colander.Str(),
        name = 'secret',
        title = _('Policy secret'),
        description = _('The secret (a string) used for auth_tkt '
                        'cookie signing'),
        required = False),

    config.SchemaNode(
        colander.Bool(),
        name = 'authorization',
        title = _('Authorization policy'),
        description = _('Enable/disable default authorization policy.'),
        required = False,
        default = True),

    title = _('Pyramid authentication settings'),
)


SESSION = config.register_settings(
    'session',

    config.SchemaNode(
        colander.Str(),
        name = 'type',
        title = _('The name of the back-end'),
        description = _('Available back-ends supplied with Beaker: file, dbm, '
                        'memory, ext:memcached, ext:database, ext:google'),
        default = ''),

    config.SchemaNode(
        colander.Str(),
        name = 'data_dir',
        title = _('Data directory'),
        description = _('Used with any back-end that stores its data in '
                        'physical files, such as the dbm or file-based '
                        'back-ends. This path should be an absolute path '
                        'to the directory that stores the files.'),
        default = ''),

    config.SchemaNode(
        colander.Str(),
        name = 'lock_dir',
        title = _('Lock directory'),
        description = _('Used with every back-end, to coordinate locking. '
                        'With caching, this lock file is used to ensure that '
                        "multiple processes/threads aren't attempting to "
                        're-create the same value at the same '
                        'time (The Dog-Pile Effect)'),
        default = ''),

    config.SchemaNode(
        colander.Str(),
        name = 'url',
        title = _('URL'),
        description = _('URL is specific to use of either ext:memcached or '
                        'ext:database. When using one of those types, '
                        'this option is required.'),
        default = ''),

    config.SchemaNode(
        colander.Str(),
        name = 'key',
        required = False,
        title = _('Key'),
        default = '',
        description = _('Name of the cookie key used to save the '
                        'session under.')),

    config.SchemaNode(
        colander.Str(),
        name = 'secret',
        required = False,
        title = _('Secret'),
        default = '',
        description = _('Used with the HMAC to ensure session integrity. '
                        'This value should ideally be a randomly '
                        'generated string.')),

    title = _('Pyramid session'),
    description = _('Beaker session configuration settings'),
    validator = (config.RequiredWithDependency('key', 'type', default=''),
                 config.RequiredWithDependency('secret', 'type', default='')),
)

SQLA = config.register_settings(
    'sqla',

    config.SchemaNode(
        colander.Str(),
        name = 'url',
        default = '',
        title = 'Engine URL',
        description = 'SQLAlchemy database engine URL'),

    config.SchemaNode(
        colander.Bool(),
        name = 'cache',
        default = True,
        title = 'Cache',
        description = 'Eanble SQLAlchemy statement caching'),

    title = 'SQLAlchemy settings',
    description = 'Configuration settings for a SQLAlchemy database engine.'
    )


MAIL = config.register_settings(
    'mail',

    config.SchemaNode(
        colander.Str(),
        name = 'host',
        title = 'Host',
        description = 'SMTP Server host name.',
        default = 'localhost'),

    config.SchemaNode(
        colander.Int(),
        name = 'port',
        title = 'Port',
        description = 'SMTP Server port number.',
        default = 25),

    config.SchemaNode(
        colander.Str(),
        name = 'username',
        title = 'Username',
        description = 'SMTP Auth username.',
        default = ''),

    config.SchemaNode(
        colander.Str(),
        name = 'password',
        title = 'Password',
        description = 'SMTP Auth password.',
        default = ''),

    config.SchemaNode(
        colander.Bool(),
        name = 'no_tls',
        title = 'No tls',
        description = 'Disable TLS.',
        default = False),

    config.SchemaNode(
        colander.Bool(),
        name = 'force_tls',
        title = 'Force TLS',
        description = 'Force use TLS.',
        default = False),

    config.SchemaNode(
        colander.Bool(),
        name = 'debug',
        title = 'Debug',
        description = 'Debug smtp.',
        default = False),

    config.SchemaNode(
        colander.Str(),
        name = 'from_name',
        default = 'Site administrator'),

    config.SchemaNode(
        colander.Str(),
        name = 'from_address',
        validator = colander.Email(),
        required = False,
        default = 'administrator@localhost.org'),

    title = 'Mail settings',
    description = 'Configuration settings for application mail.',
)
