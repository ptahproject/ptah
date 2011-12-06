""" ptah settings """
import uuid
import pytz
import sqlahelper
import sqlalchemy
import translationstring
from email.utils import formataddr
from pyramid.compat import bytes_
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.interfaces import IAuthorizationPolicy
from pyramid.interfaces import IAuthenticationPolicy
from pyramid.interfaces import ISessionFactory

import ptah
from ptah import manage
from ptah.security import get_local_roles


_ = translationstring.TranslationStringFactory('ptah')


ptah.register_settings(
    ptah.CFG_ID_PTAH,

    ptah.form.BoolField(
        'auth',
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

    ptah.form.IntegerField(
        'settings_dbpoll',
        title = _('Settings db poll interval (seconds).'),
        description = _('If you allow to change setting ttw. '
                        '"0" means do not poll'),
        default = 0),

    ptah.form.BoolField(
        'chameleon_reload',
        default = False,
        title = 'Auto reload',
        description = 'Enable chameleon templates auto reload.'),

    ptah.form.TextField(
        'static_url',
        default = 'static'),

    ptah.form.IntegerField(
        'static_cache_max_age',
        default = 0),

    ptah.form.TextField(
        'manage',
        title = 'Ptah manage id',
        default = 'ptah-manage'),

    ptah.form.LinesField(
        'managers',
        title = 'Managers',
        description = 'List of user logins with access rights to '\
                            'ptah management ui.',
        default = ()),

    ptah.form.LinesField(
        'disable_modules',
        title = 'Hide Modules in Management UI',
        description = 'List of modules names to hide in manage ui',
        default = ()),

    ptah.form.LinesField(
        'disable_models',
        title = 'Hide Models in Model Management UI',
        description = 'List of models to hide in model manage ui',
        default = ()),

    title = _('Ptah settings'),
)

ptah.register_settings(
    ptah.CFG_ID_SESSION,

    ptah.form.BoolField(
        'enabled',
        title = _('Enable beaker session'),
        default = False),

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

    ttw = True,
    title = 'Site formats',
    )


ptah.register_settings(
    ptah.CFG_ID_PASSWORD,

    form.TextField(
        name = 'manager',
        title = 'Password manager',
        description = 'Available password managers '\
            '("plain", "ssha", "bcrypt")',
        default = 'plain'),

    form.IntegerField(
        'min_length',
        title = 'Length',
        description = 'Password minimium length.',
        default = 5),

    form.BoolField(
        'letters_digits',
        title = 'Letters and digits',
        description = 'Use letters and digits in password.',
        default = False),

    form.BoolField(
        'letters_mixed_case',
        title = 'Letters mixed case',
        description = 'Use letters in mixed case.',
        default = False),

    title = 'Password tool settings',
    )


@ptah.subscriber(ptah.events.SettingsInitialized)
def initialized(ev):
    # auth
    PTAH = ptah.get_settings(ptah.CFG_ID_PTAH, ev.registry)
    if PTAH['auth']:
        kwargs = {'wild_domain': False,
                  'callback': get_local_roles}

        policy = AuthTktAuthenticationPolicy(
            secret = PTAH['secret'], **kwargs)
        ev.registry.registerUtility(policy, IAuthenticationPolicy)

    if PTAH['authorization']:
        ev.registry.registerUtility(
            ACLAuthorizationPolicy(), IAuthorizationPolicy)

    # mail
    try:
        from repoze.sendmail import mailer
        from repoze.sendmail import delivery
    except ImportError: # pragma: no cover
        pass
    else:
        MAIL = ptah.get_settings(ptah.CFG_ID_MAIL, ev.registry)
        smtp_mailer = mailer.SMTPMailer(
            hostname = MAIL['host'],
            port = MAIL['port'],
            username = MAIL['username']or None,
            password = MAIL['password'] or None,
            no_tls = MAIL['no_tls'],
            force_tls = MAIL['force_tls'],
            debug_smtp = MAIL['debug'])

        MAIL['Mailer'] = delivery.DirectMailDelivery(smtp_mailer)
        MAIL['full_from_address'] = formataddr(
            (MAIL['from_name'], MAIL['from_address']))

    # sqla
    SQLA = ptah.get_settings(ptah.CFG_ID_SQLA, ev.registry)
    url = SQLA['url']
    if url:
        engine_args = {}
        if SQLA['cache']:
            cache = {}
            engine_args['execution_options'] = \
                {'compiled_cache': cache}
            SQLA['sqlalchemy_cache'] = cache
        try:
            engine = sqlahelper.get_engine()
        except: # pragma: no cover
            engine = sqlalchemy.engine_from_config(
                {'sqlalchemy.url': url}, 'sqlalchemy.', **engine_args)
            sqlahelper.add_engine(engine)


    # session
    SESSION = ptah.get_settings(ptah.CFG_ID_SESSION, ev.registry)
    if SESSION['enabled']:
        settings = dict(('session.%s'%key, val) for key, val in
                        SESSION.items() if val)
        if 'session.secret' in settings:
            settings['session.secret'] = bytes_(
                settings['session.secret'], 'utf8')

        try:
            import pyramid_beaker
        except ImportError: # pragma: no cover
            pass
        else:
            session_factory = pyramid_beaker\
                .session_factory_from_settings(settings)
            ev.config.set_session_factory(session_factory)

    # ptah manage
    if PTAH['manage']:
        ev.config.add_route(
            'ptah-manage', '/ptah-manage/*traverse',
            factory=ptah.manage.PtahManageRoute, use_global_views=True)

    # chameleon
    import chameleon.template
    chameleon.template.AUTO_RELOAD=PTAH['chameleon_reload']
    chameleon.template.BaseTemplateFile.auto_reload=PTAH['chameleon_reload']
