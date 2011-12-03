""" ptah settings """
import ptah
import pytz
import translationstring

_ = translationstring.TranslationStringFactory('ptah')


ptah.register_settings(
    ptah.CFG_ID_AUTH,

    ptah.form.BoolField(
        'policy',
        title = _('Authentication policy'),
        description = _('Enable authentication policy.'),
        default = False),

    ptah.form.TextField(
        'secret',
        title = _('Policy secret'),
        description = _('The secret (a string) used for auth_tkt '
                        'cookie signing'),
        default = ''),

    ptah.form.BoolField(
        'authorization',
        title = _('Authorization policy'),
        description = _('Enable/disable default authorization policy.'),
        default = True),

    title = _('Pyramid authentication settings'),
)


ptah.register_settings(
    ptah.CFG_ID_SESSION,

    ptah.form.TextField(
        'type',
        title = _('The name of the back-end'),
        description = _('Available back-ends supplied with Beaker: file, dbm, '
                        'memory, ext:memcached, ext:database, ext:google'),
        default = ''),

    ptah.form.TextField(
        'data_dir',
        title = _('Data directory'),
        description = _('Used with any back-end that stores its data in '
                        'physical files, such as the dbm or file-based '
                        'back-ends. This path should be an absolute path '
                        'to the directory that stores the files.'),
        default = ''),

    ptah.form.TextField(
        'lock_dir',
        title = _('Lock directory'),
        description = _('Used with every back-end, to coordinate locking. '
                        'With caching, this lock file is used to ensure that '
                        "multiple processes/threads aren't attempting to "
                        're-create the same value at the same '
                        'time (The Dog-Pile Effect)'),
        default = ''),

    ptah.form.TextField(
        'url',
        title = _('URL'),
        description = _('URL is specific to use of either ext:memcached or '
                        'ext:database. When using one of those types, '
                        'this option is required.'),
        default = ''),

    ptah.form.TextField(
        'key',
        title = _('Key'),
        default = '',
        description = _('Name of the cookie key used to save the '
                        'session under.')),

    ptah.form.TextField(
        'secret',
        title = _('Secret'),
        default = '',
        description = _('Used with the HMAC to ensure session integrity. '
                        'This value should ideally be a randomly '
                        'generated string.')),

    title = _('Pyramid session'),
    description = _('Beaker session configuration settings'),
    #validator = (config.RequiredWithDependency('key', 'type', default=''),
    #             config.RequiredWithDependency('secret', 'type', default='')),
)

ptah.register_settings(
    ptah.CFG_ID_SQLA,

    ptah.form.TextField(
        'url',
        default = '',
        title = 'Engine URL',
        description = 'SQLAlchemy database engine URL'),

    ptah.form.BoolField(
        'cache',
        default = True,
        title = 'Cache',
        description = 'Eanble SQLAlchemy statement caching'),

    title = 'SQLAlchemy settings',
    description = 'Configuration settings for a SQLAlchemy database engine.'
    )


ptah.register_settings(
    ptah.CFG_ID_MAIL,

    ptah.form.TextField(
        'host',
        title = 'Host',
        description = 'SMTP Server host name.',
        default = 'localhost'),

    ptah.form.IntegerField(
        'port',
        title = 'Port',
        description = 'SMTP Server port number.',
        default = 25),

    ptah.form.TextField(
        'username',
        title = 'Username',
        description = 'SMTP Auth username.',
        default = ''),

    ptah.form.TextField(
        'password',
        title = 'Password',
        description = 'SMTP Auth password.',
        default = ''),

    ptah.form.BoolField(
        'no_tls',
        title = 'No tls',
        description = 'Disable TLS.',
        default = False),

    ptah.form.BoolField(
        'force_tls',
        title = 'Force TLS',
        description = 'Force use TLS.',
        default = False),

    ptah.form.BoolField(
        'debug',
        title = 'Debug',
        description = 'Debug smtp.',
        default = False),

    ptah.form.TextField(
        'from_name',
        default = 'Site administrator'),

    ptah.form.TextField(
        'from_address',
        validator = ptah.form.Email(),
        required = False,
        default = 'administrator@localhost.org'),

    title = 'Mail settings',
    description = 'Configuration settings for application mail.',
)


ptah.register_settings(
    ptah.CFG_ID_VIEW,

    ptah.form.TextField(
        'static_url',
        default = 'static'),

    ptah.form.IntegerField(
        'cache_max_age',
        default = 0),

    ptah.form.BoolField(
        'chameleon_reload',
        default = False,
        title = 'Auto reload',
        description = 'Enable chameleon templates auto reload.'),

    title = 'Ptah view configuration',
)


ptah.register_settings(
    ptah.CFG_ID_FORMAT,

    ptah.form.TimezoneField(
        'timezone',
        default = pytz.timezone('US/Central'),
        title = _('Timezone'),
        description = _('Site wide timezone.')),

    ptah.form.TextField(
        'date_short',
        default = '%m/%d/%y',
        title = _('Date'),
        description = _('Date short format')),

    ptah.form.TextField(
        'date_medium',
        default = '%b %d, %Y',
        title = _('Date'),
        description = _('Date medium format')),

    ptah.form.TextField(
        'date_long',
        default = '%B %d, %Y',
        title = _('Date'),
        description = _('Date long format')),

    ptah.form.TextField(
        'date_full',
        default = '%A, %B %d, %Y',
        title = _('Date'),
        description = _('Date full format')),

    ptah.form.TextField(
        'time_short',
        default = '%I:%M %p',
        title = _('Time'),
        description = _('Time short format')),

    ptah.form.TextField(
        'time_medium',
        default = '%I:%M %p',
        title = _('Time'),
        description = _('Time medium format')),

    ptah.form.TextField(
        'time_long',
        default = '%I:%M %p %z',
        title = _('Time'),
        description = _('Time long format')),

    ptah.form.TextField(
        'time_full',
        default = '%I:%M:%S %p %Z',
        title = _('Time'),
        description = _('Time full format')),

    title = 'Site formats',
    )
