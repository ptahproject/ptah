""" basic app settings """
import colander
import pyramid_sqla
import pyramid_beaker
import translationstring
from memphis import config
from pyramid.interfaces import IAuthenticationPolicy
from pyramid.authentication import AuthTktAuthenticationPolicy

_ = translationstring.TranslationStringFactory('ptah')

types = {
    '': (),
    'auth_tkt': (AuthTktAuthenticationPolicy,
                 ('secret',)),
}

SEQURITY = config.registerSettings(
    'auth',

    config.SchemaNode(
        colander.Str(),
        name = 'policy',
        title = _('Authentication policy'),
        validator = colander.OneOf(types.keys()),
        required = False,
        default = ''),

    config.SchemaNode(
        colander.Str(),
        name = 'secret',
        title = _('Policy secret'),
        description = _('The secret (a string) used for auth_tkt '
                        'cookie signing'),
        required = False),

    title = _('Pyramid authentication settings'),
    validator = config.RequiredWithDependency('secret','policy','auth_tkt',''),
)

SESSION = config.registerSettings(
    'session',

    config.SchemaNode(
        colander.Str(),
        name = 'type',
        title = _('The name of the back-end'),
        description = _('Available back-ends supplied with Beaker: file, dbm, memory, ext:memcached, ext:database, ext:google'),
        default = ''),

    config.SchemaNode(
        colander.Str(),
        name = 'data_dir',
        title = _('Data directory'),
        description = _('Used with any back-end that stores its data in physical files, such as the dbm or file-based back-ends. This path should be an absolute path to the directory that stores the files.'),
        default = ''),

    config.SchemaNode(
        colander.Str(),
        name = 'lock_dir',
        title = _('Lock directory'),
        description = _("Used with every back-end, to coordinate locking. With caching, this lock file is used to ensure that multiple processes/threads aren't attempting to re-create the same value at the same time (The Dog-Pile Effect)"),
        default = ''),

    config.SchemaNode(
        colander.Str(),
        name = 'url',
        title = _('URL'),
        description = _('URL is specific to use of either ext:memcached or ext:database. When using one of those types, this option is required.'),
        default = ''),

    config.SchemaNode(
        colander.Str(),
        name = 'key',
        required = False,
        title = _('Key'),
        default = '',
        description = _('Name of the cookie key used to save the session under.')),

    config.SchemaNode(
        colander.Str(),
        name = 'secret',
        required = False,
        title = _('Secret'),
        default = '',
        description = _('Used with the HMAC to ensure session integrity. This value should ideally be a randomly generated string.')),
    
    title = _('Pyramid session'),
    description = _('Beaker session configuration settings'),
    validator = (config.RequiredWithDependency('key', 'type', default=''),
                 config.RequiredWithDependency('secret', 'type', default='')),
)

SQLA = config.registerSettings(
    'sqla',

    config.SchemaNode(
        colander.Str(),
        name = 'url',
        default = '',
        title = 'Engine URL',
        description = 'SQLAlchemy database engine URL'),
    
    title = 'SQLAlchemy settings',
    description = 'Configuration settings for a SQLAlchemy database engine.'
    )


@config.handler(config.SettingsInitializing)
def initializing(ev):
    if pyramid_sqla is not None:
        url = SQLA.url
        if url:
            pyramid_sqla.add_engine({'sqlalchemy.url': url})


@config.handler(config.SettingsInitializing)
def initializing(ev):
    config = ev.config

    if config is not None:
        # auth
        pname = SEQURITY.policy
        if pname not in ('', 'no-policy'):
            policyFactory, attrs = types[pname]

            settings = []
            for attr in attrs:
                settings.append(SEQURITY.get(attr))

            policy = policyFactory(*settings)
            config.registry.registerUtility(policy, IAuthenticationPolicy)

        # session
        session_factory = pyramid_beaker \
            .session_factory_from_settings(SESSION)
        config.set_session_factory(session_factory)

    url = SQLA.url
    if url:
        pyramid_sqla.add_engine({'sqlalchemy.url': url})
