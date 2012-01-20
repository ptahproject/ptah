""" ptah settings """
import pytz
import logging
import sqlalchemy
import translationstring
from email.utils import formataddr

from pyramid.compat import bytes_
from pyramid.events import ApplicationCreated

import ptah
from ptah import manage, settings

_ = translationstring.TranslationStringFactory('ptah')

log = logging.getLogger('ptah')


ptah.register_settings(
    ptah.CFG_ID_PTAH,

    ptah.form.BoolField(
        'auth',
        title = _('Authentication policy'),
        description = _('Enable authentication policy.'),
        default = False),

    ptah.form.TextField(
        'secret',
        title = _('Authentication policy secret'),
        description = _('The secret (a string) used for auth_tkt '
                        'cookie signing'),
        default = '',
        tint = True),

    ptah.form.TextField(
        'manage',
        title = 'Ptah manage id',
        default = 'ptah-manage'),

    ptah.form.LinesField(
        'managers',
        title = 'Manage login',
        description = 'List of user logins with access rights to '\
                            'ptah management ui.',
        default = ()),

    ptah.form.TextField(
        'manager_role',
        title = 'Manager role',
        description = 'Specific role with access rights to ptah management ui.',
        default = ''),

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

    ptah.form.TextField(
        'email_from_name',
        default = 'Site administrator'),

    ptah.form.TextField(
        'email_from_address',
        validator = ptah.form.Email(),
        required = False,
        default = 'admin@localhost'),

    ptah.form.ChoiceField(
        'pwd_manager',
        title = 'Password manager',
        description = 'Available password managers '\
            '("plain", "ssha", "bcrypt")',
        vocabulary = ptah.form.SimpleVocabulary.from_values(
            "plain", "ssha",),
        default = 'plain'),

    ptah.form.IntegerField(
        'pwd_min_length',
        title = 'Length',
        description = 'Password minimium length.',
        default = 5),

    ptah.form.BoolField(
        'pwd_letters_digits',
        title = 'Letters and digits',
        description = 'Use letters and digits in password.',
        default = False),

    ptah.form.BoolField(
        'pwd_letters_mixed_case',
        title = 'Letters mixed case',
        description = 'Use letters in mixed case.',
        default = False),

    ptah.form.LinesField(
        'db_skip_tables',
        title = 'Skip table creation',
        description = 'Do not create listed tables during data population.',
        default = ()),

    ptah.form.LinesField(
        'default_roles',
        title = 'Default roles',
        description = 'List of default assigned roles for all principals.',
        default = ()),

    title = _('Ptah settings'),
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


def set_mailer(cfg, mailer):
    def action(cfg, mailer):
        PTAH = ptah.get_settings(ptah.CFG_ID_PTAH, cfg.registry)
        PTAH['Mailer'] = mailer

    cfg.action('ptah.ptah_mailer', action, (cfg, mailer))


class DummyMailer(object):

    def send(self, from_, to_, message):
        log.warning("Mailer is not configured.")
        log.warning(message)


@ptah.subscriber(ptah.events.SettingsInitializing)
def initialized(ev):
    PTAH = ptah.get_settings(ptah.CFG_ID_PTAH, ev.registry)

    # mail
    if PTAH.get('Mailer') is None:
        PTAH['Mailer'] = DummyMailer()
        PTAH['full_email_address'] = formataddr(
            (PTAH['email_from_name'], PTAH['email_from_address']))


def enable_manage(cfg, name='ptah-manage', access_manager=None,
                  managers=None, manager_role=None, disable_modules=None):
    """Implementation for pyramid `ptah_init_manage` directive """
    def action(cfg, name, access_manager,
               managers, manager_role, disable_modules):
        PTAH = cfg.ptah_get_settings(ptah.CFG_ID_PTAH)

        PTAH['manage'] = name
        if managers is not None:
            PTAH['managers'] = managers
        if manager_role is not None:
            PTAH['manager_role'] = manager_role
        if disable_modules is not None:
            PTAH['disable_modules'] = disable_modules

        if access_manager is None:
            access_manager = ptah.manage.PtahAccessManager(cfg.registry)

        ptah.manage.set_access_manager(access_manager, cfg.registry)

    cfg.add_route('ptah-manage', '/{0}/*traverse'.format(name),
                  factory=ptah.manage.PtahManageRoute, use_global_views=True)
    cfg.action(
        'ptah.ptah_manage', action,
        (cfg, name, access_manager,
         managers, manager_role, disable_modules), order=999999+1)


def initialize_sql(cfg, prefix='sqlalchemy.'):
    def action(cfg, cache):
        PTAH = cfg.ptah_get_settings(ptah.CFG_ID_PTAH)
        PTAH['sqlalchemy_cache'] = {}
        PTAH['sqlalchemy_initialized'] = True

    cache = {}
    engine = sqlalchemy.engine_from_config(
        cfg.registry.settings, prefix,
        execution_options = {'compiled_cache': cache, 'echo': True})

    ptah.get_session().configure(bind=engine)
    ptah.get_base().metadata.bind = engine

    cfg.action('ptah.initalize_sql', action, (cfg, cache))

    # check_version
    from ptah import migrate
    cfg.add_subscriber(migrate.check_version, ApplicationCreated)


@ptah.subscriber(ApplicationCreated)
def starting(ev):
    session = ptah.get_session()
    if not (session.bind and settings.SettingRecord.__table__.exists()):
        return

    # load db settings
    s_ob = ptah.config.get_cfg_storage(
        settings.SETTINGS_OB_ID, default_factory=settings.Settings)
    s_ob.load_fromdb()
