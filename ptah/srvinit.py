""" basic app settings """
import uuid
import sqlahelper
import sqlalchemy
import pyramid_beaker
from email.Utils import formataddr
from pyramid.interfaces import IAuthenticationPolicy, IAuthorizationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.authentication import AuthTktAuthenticationPolicy
from repoze.sendmail.mailer import SMTPMailer
from repoze.sendmail.delivery import DirectMailDelivery

from ptah import config
from ptah.security import get_local_roles
from ptah.settings import types, PTAH_CONFIG, MAIL, SESSION, SECURITY, SQLA

SQL_compiled_cache = {}


@config.subscriber(config.SettingsInitializing)
def initializing(ev):
    # auth
    if not SECURITY.secret:
        SECURITY.secret = uuid.uuid4().get_hex()

    pname = SECURITY.policy
    if pname not in ('', 'no-policy'):
        policyFactory, attrs, kw = types[pname]

        settings = []
        for attr in attrs:
            settings.append(SECURITY.get(attr))

        kwargs = {'wild_domain': False,
                  'callback': get_local_roles}
        for attr in kw:
            kwargs[attr] = SECURITY.get(attr)

        policy = policyFactory(*settings, **kwargs)
        config.registry.registerUtility(policy, IAuthenticationPolicy)

    if SECURITY.authorization:
        config.registry.registerUtility(
            ACLAuthorizationPolicy(), IAuthorizationPolicy)

    # mail
    smtp_mailer = SMTPMailer(
        hostname = MAIL.host,
        port = MAIL.port,
        username = MAIL.username or None,
        password = MAIL.password or None,
        no_tls = MAIL.no_tls,
        force_tls = MAIL.force_tls,
        debug_smtp = MAIL.debug)

    MAIL.Mailer = DirectMailDelivery(smtp_mailer)
    MAIL.full_from_address = formataddr((MAIL.from_name, MAIL.from_address))

    # sqla
    url = SQLA.url
    if url:
        engine_args = {}
        if SQLA.cache:
            engine_args['execution_options'] = \
                {'compiled_cache': SQL_compiled_cache}
        try:
            engine = sqlahelper.get_engine()
        except:
            engine = sqlalchemy.engine_from_config(
                {'sqlalchemy.url': url}, 'sqlalchemy.', **engine_args)
            sqlahelper.add_engine(engine)


@config.subscriber(config.AppStarting)
def start(ev):
    # session
    settings = dict(('session.%s'%key, val) for key, val in
                    SESSION.items() if val)
    session_factory = pyramid_beaker \
       .session_factory_from_settings(settings)
    ev.config.set_session_factory(session_factory)
