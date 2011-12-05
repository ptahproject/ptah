""" settings """
import logging
import os.path
import sqlahelper as sqlh
import sqlalchemy as sqla
from collections import OrderedDict

from zope import interface
from zope.interface.interface import InterfaceClass
from pyramid.compat import configparser

import ptah
from ptah import uri, form, config
from ptah.config import StopException
from ptah.config import subscriber, DirectiveInfo, Action

log = logging.getLogger('ptah')

SETTINGS_ID = 'settings'
SETTINGS_OB_ID = 'ptah:settings'
SETTINGS_GROUP_ID = 'ptah:settings-group'


_marker = object()


def get_settings(grp, registry=None):
    """ get settings group by group id """
    return config.get_cfg_storage(SETTINGS_GROUP_ID, registry)[grp]


@uri.resolver('settings')
def settings_resolver(uri):
    """ Ptah settings resolver """
    return config.get_cfg_storage(SETTINGS_GROUP_ID)[uri[9:]]


def pyramid_get_settings(config, grp):
    return config.get_cfg_storage(SETTINGS_GROUP_ID)[grp]


def initialize_settings(pconfig, cfg, section=configparser.DEFAULTSECT):
    registry = pconfig.registry
    settings = config.get_cfg_storage(SETTINGS_OB_ID, pconfig.registry, Settings)

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
        config.notify(ptah.events.SettingsInitializing(pconfig, pconfig.registry))
        config.notify(ptah.events.SettingsInitialized(pconfig, pconfig.registry))
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
            raise StopException(
              'Default value is required for "{0}.{1}"'.format(name,field.name))

    group = Group(name=name, *fields, **kw)
    interface.directlyProvides(Group, category)

    ac = Action(
        lambda config, group: config.get_cfg_storage(SETTINGS_GROUP_ID)\
            .update({group.__name__: group.clone(config.registry)}),
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

        self.load(defaults, True)

    def load(self, rawdata, setdefaults=False):
        groups = config.get_cfg_storage(SETTINGS_GROUP_ID).items()

        try:
            rawdata = dict((k.lower(), v) for k, v in rawdata.items())
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

    def load_fromdb(self):
        self.load(dict(Session.query(SettingRecord.name,SettingRecord.value)))

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
        self.__uri__ = 'settings:{0}'.format(fields.name)
        self.__name__ = fields.name
        self.__title__ = fields.title
        self.__description__ = fields.description
        self.__fields__ = fields
        self.__ttw__ = kwargs.get('ttw', False)
        self.__ttw_skip_fields__ = kwargs.get('ttw_skip_fields', False)

    def clone(self, registry):
        clone = self.__class__.__new__(self.__class__)
        clone.__dict__.update(self.__dict__)
        clone.__registry__ = registry
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

    def updatedb(self, **data):
        self.update(data)

        name = self.__name__
        fields = self.__fields__

        # remove old data
        keys = tuple('{0}.{1}'.format(name, key) for key in data.keys())
        if keys:
            Session.query(SettingRecord)\
                .filter(SettingRecord.name.in_(keys)).delete(False)

        # insert new data
        result = []
        for fname in data.keys():
            if fname not in fields:
                continue

            field = fields[fname]
            value = self[fname]
            if value == field.default:
                continue

            result.append(
                {'name': '{0}.{1}'.format(name,fname),
                 'value': field.dumps(value)})
            Session.add(
                SettingRecord(name='{0}.{1}'.format(name,fname),
                              value=field.dumps(value)))
        Session.flush()

        self.__registry__.notify(ptah.events.SettingsGroupModified(self))


Session = sqlh.get_session()

class SettingRecord(sqlh.get_base()):

    __tablename__ = 'ptah_settings'

    name = sqla.Column(sqla.String, primary_key=True)
    value = sqla.Column(sqla.String)
