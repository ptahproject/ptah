""" settings """
import logging
import os.path
from collections import OrderedDict

from zope import interface
from zope.interface.interface import InterfaceClass
from pyramid.compat import configparser

from ptah import form, config
from ptah.config import StopException
from ptah.config.directives import event, subscriber, DirectiveInfo, Action

log = logging.getLogger('ptah.config')


class SettingsInitializing(object):
    """ Settings initializing event """
    event('Settings initializing event')

    config = None
    registry = None

    def __init__(self, config, registry):
        self.config = config
        self.registry = registry


class SettingsInitialized(object):
    """ ptah sends this event when settings initialization is completed. """
    event('Settings initialized event')

    config = None
    registry = None

    def __init__(self, config, registry):
        self.config = config
        self.registry = registry


_marker = object()

SETTINGS_ID = 'settings'
SETTINGS_OB_ID = 'ptah:settings'
SETTINGS_GROUP_ID = 'ptah:settings-group'


def get_settings(grp, registry=None):
    """ get settings group by group id """
    return config.get_cfg_storage(SETTINGS_GROUP_ID, registry)[grp]


def pyramid_get_settings(config, grp):
    return config.get_cfg_storage(SETTINGS_GROUP_ID)[grp]


@subscriber(config.Initialized)
def init_settings(ev):
    registry = ev.config.registry

    settings = Settings()
    registry.__ptah_storage__[SETTINGS_OB_ID] = settings


def initialize_settings(pconfig, cfg, section=configparser.DEFAULTSECT):
    settings = pconfig.registry.__ptah_storage__[SETTINGS_OB_ID]
    if settings.initialized:
        raise RuntimeError(
            "initialize_settings has been called more than once.")

    log.info('Initializing ptah settings')

    settings.initialized = True

    if cfg:
        here = cfg.get('here', './')

        include = cfg.get('include', '')
        for f in include.split('\n'):
            f = f.strip()
            if f and os.path.exists(f):
                parser = configparser.SafeConfigParser()
                parser.read(f)
                if section == configparser.DEFAULTSECT or \
                       parser.has_section(section):
                    cfg.update(parser.items(section, vars={'here': here}))

    pconfig.begin()
    try:
        settings.init(pconfig, cfg)
        config.notify(SettingsInitializing(pconfig, pconfig.registry))
        config.notify(SettingsInitialized(pconfig, pconfig.registry))
    except Exception as e:
        raise StopException(e)
    finally:
        pconfig.end()


def register_settings(name, *fields, **kw):
    iname = name
    for ch in ('.', '-'):
        iname = iname.replace(ch, '_')

    category = InterfaceClass(
        'SettingsGroup:%s' % iname.upper(), (),
        __doc__='Settings group: %s' % name,
        __module__='ptah.config.settings')

    for field in fields:
        field.required = False
        if field.default is form.null:
            raise StopException('field.default could not be "null"')

    group = Group(name=name, *fields, **kw)
    interface.directlyProvides(Group, category)

    ac = Action(
        lambda config, group: config.get_cfg_storage(SETTINGS_GROUP_ID)\
            .update({group.__name__: group.clone()}),
        (group,),
        discriminator=(SETTINGS_GROUP_ID, name))

    info = DirectiveInfo()
    info.attach(ac)

    return group


class Settings(object):
    """ settings management system """

    initialized = False

    def init(self, config, defaults=None):
        groups = config.get_cfg_storage(SETTINGS_GROUP_ID).items()

        for name, group in groups:
            data = {}
            for field in group.__fields__.values():
                if field.default is not form.null:
                    data[field.name] = field.default

            group.update(data)

        if defaults is None:
            return

        # load defaults
        try:
            rawdata = dict((k.lower(), v) for k, v in defaults.items())
        except Exception as e:
            raise StopException(e)

        for name, group in groups:
            data, errors = group.extract(rawdata)

            if errors:
                log.error(errors.msg)
                raise StopException(errors)

            for k, v in data.items():
                if v is not form.null:
                    group.__fields__[k].default = v

            group.update(data)

    def export(self, default=False):
        groups = config.get_cfg_storage(SETTINGS_GROUP_ID).items()

        result = {}
        for name, group in groups:
            for field in group.__fields__.values():
                fname = field.name
                if group[fname] == field.default and not default:
                    continue

                result['{0}.{1}'.format(name,fname)] = field.dumps(group[fname])

        return result


class Group(OrderedDict):

    def __init__(self, *args, **kwargs):
        super(Group, self).__init__()

        fields = form.Fieldset(*args, **kwargs)
        self.__name__ = fields.name
        self.__title__ = fields.title
        self.__description__ = fields.description
        self.__fields__ = fields

    def clone(self):
        clone = self.__class__.__new__(self.__class__)
        clone.__dict__.update(self.__dict__)
        return clone

    def extract(self, rawdata):
        fieldset = self.__fields__
        name = fieldset.name

        data = {}
        errors = form.FieldsetErrors(fieldset)

        for field in fieldset.fields():
            value = rawdata.get('{0}.{1}'.format(name, field.name), _marker)

            if value is _marker:
                value = field.default
            else:
                try:
                    value = field.loads(value)
                    field.validate(value)

                    if field.preparer is not None:
                        value = field.preparer(value)
                except form.Invalid as e:
                    errors.append(e)
                    value = field.default

            data[field.name] = value

        if not errors:
            try:
                fieldset.validate(data)
            except form.Invalid as e:
                errors.append(e)

        return data, errors

    def get(self, name, default=None):
        try:
            return super(Group, self).__getitem__(name)
        except (KeyError, AttributeError):
            pass

        if name in self.__fields__:
            return self.__fields__[name].default

        return default

    def keys(self):
        return [node.name for node in self.__fields__.values()]

    def items(self):
        return [(key, self.get(key)) for key in self.__fields__.keys()]

    def __getitem__(self, name):
        res = self.get(name, _marker)
        if res is _marker:
            raise KeyError(name)
        return res
