""" mail settings """
import colander
from email.Utils import formataddr
from repoze.sendmail.mailer import SMTPMailer
from repoze.sendmail.delivery import DirectMailDelivery

from memphis import config


MAIL = config.registerSettings(
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


@config.handler(config.SettingsInitializing)
def initializing(ev):
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


@config.handler(MAIL.category, config.SettingsGroupModified)
def mailSettingsModified(group, ev):
    print '--------------'
