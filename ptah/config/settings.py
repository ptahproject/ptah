""" settings """
import colander
import ConfigParser
import logging
import os.path

from zope import interface
from zope.interface.interface import InterfaceClass

import api
import schema
from directives import event, subscriber, DirectiveInfo, Action

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
SETTINGS_OB_ID = 'ptah.config:settings'
SETTINGS_GROUP_ID = 'ptah.config:settings-group'


def get_settings():
    return api.get_cfg_storage(SETTINGS_OB_ID)


@subscriber(api.Initialized)
def init_settings(ev):
    settings = Settings()
    ev.registry.storage[SETTINGS_OB_ID] = settings

    # complete settings initialization
    for grp in ev.registry.storage[SETTINGS_GROUP_ID].values():
        settings.register(grp)


def initialize_settings(cfg, pconfig, section=ConfigParser.DEFAULTSECT):
    settings = pconfig.registry.storage[SETTINGS_OB_ID]
    if settings.initialized:
        raise RuntimeError(
            "initialize_settings has been called more than once.")

    log.info('Initializing ptah settings')

    settings.config = pconfig
    settings.initialized = True

    here = cfg.get('here', './')

    include = cfg.get('include', '')
    for f in include.split('\n'):
        f = f.strip()
        if f and os.path.exists(f):
            parser = ConfigParser.SafeConfigParser()
            parser.read(f)
            if section == ConfigParser.DEFAULTSECT or \
                    parser.has_section(section):
                cfg.update(parser.items(section, vars={'here': here}))

    pconfig.begin()
    try:
        settings.init(cfg)
        api.notify(SettingsInitializing(pconfig, pconfig.registry))
        api.notify(SettingsInitialized(pconfig, pconfig.registry))
    except Exception, e:
        raise api.StopException(e)
    finally:
        pconfig.end()


def register_settings(name, *nodes, **kw):
    title = kw.get('title', '')
    description = kw.get('description', '')
    validator = kw.get('validator', None)

    iname = name
    for ch in ('.', '-'):
        iname = iname.replace(ch, '_')

    category = InterfaceClass(
        'SettingsGroup:%s' % iname.upper(), (),
        __doc__='Settings group: %s' % name,
        __module__='ptah.config.settings')

    group = Group(name, title, description, category, *nodes)

    if validator is not None:
        if type(validator) not in (list, tuple):
            validator = validator,

        for v in validator:
            group.schema.validator.add(v)

    ac = Action(
        lambda config, group: config.get_cfg_storage(SETTINGS_GROUP_ID)\
            .update({group.name: group}),
        (group,),
        discriminator=(SETTINGS_GROUP_ID, name))

    info = DirectiveInfo()
    info.attach(ac)

    return group


class Settings(dict):
    """ settings management system """

    config = None
    initialized = False

    def __init__(self):
        self.schema = schema.SchemaNode(schema.Mapping())

    def _load(self, rawdata, setdefaults=False):
        try:
            rawdata = dict((k.lower(), v) for k, v in rawdata.items())
            data = self.schema.unflatten(rawdata)
        except Exception, exc:
            log.error('Error loading settings: %s', exc)
            if setdefaults:
                raise
            return

        try:
            data = self.schema.deserialize(data)
        except colander.Invalid, e:
            errs = e.asdict()
            if setdefaults:
                log.error('Error loading default settings: \n%s' % (
                        '\n'.join('%s: %s' % (k, v) for k, v in errs.items())))
                return

            log.error('Error loading settings, reloading with defaults: \n%s' %
                    ('\n'.join('%s: %s' % (k, v) for k, v in errs.items())))

            defaults = self.schema.flatten(self.schema.serialize())

            for k in errs.keys():
                rawdata.pop(k)
                rawdata[k] = defaults[k]

            data = self.schema.deserialize(self.schema.unflatten(rawdata))

        for name, group in self.items():
            if name in data and data[name]:
                if setdefaults:
                    for k, v in data[name].items():
                        if v is not colander.null:
                            group.schema[k].default = v

                group.update(data[name])

    def init(self, defaults=None):
        for group in self.values():
            data = {}
            for node in group.schema.children:
                node.default = node._origin_default
                if node.default is not colander.null:
                    data[node.name] = node.default

            group.update(data)

        if defaults:
            self._load(defaults, True)

    def export(self, default=False):
        result = {}
        for name, group in self.items():
            data = dict((node.name, node.default) for node in group.schema)
            data.update(group.items())
            result[name] = data

        result = self.schema.serialize(result)

        if not default:
            for prefix, group in self.items():
                schema = group.schema
                for key, val in group.items():
                    if val == schema[key].default:
                        del result[prefix][key]

        return self.schema.flatten(result)

    def register(self, group):
        if group.name not in self:
            self.schema.add(group.schema)
            self[group.name] = group


class GroupValidator(object):

    def __init__(self):
        self._validators = []

    def add(self, validator):
        if validator not in self._validators:
            self._validators.append(validator)

    def __call__(self, node, appstruct):
        error = None
        for validator in self._validators:
            try:
                validator(node, appstruct)
            except colander.Invalid, e:
                if error is None:
                    error = colander.Invalid(node)

                if e.node is node:
                    error.add(e)
                else:
                    error.add(e, node.children.index(e.node))

        if error is not None:
            raise error


class Group(object):

    def __init__(self, name, title, description, category, *nodes):
        self.name = name
        self.title = title
        self.description = description
        self.category = category
        self.schema = schema.SchemaNode(
            schema.Mapping(),
            name=name,
            required=False,
            validator=GroupValidator())

        interface.directlyProvides(self, category)

        for node in nodes:
            if not isinstance(node, schema.SchemaNode):
                raise RuntimeError(
                    "Node '%s' has to be instance of "
                    "ptah.config.SchemaNode" % node.name)

            self.schema.add(node)

    def get(self, name, default=None):
        try:
            data = api.get_cfg_storage(SETTINGS_ID)[self.name]
            if name in data:
                return data[name]
        except (KeyError, AttributeError):
            pass

        if name in self.schema:
            return self.schema[name].default

        return default

    def keys(self):
        return [node.name for node in self.schema]

    def items(self):
        return [(key, self.get(key)) for key in self.keys()]

    def update(self, data):
        api.get_cfg_storage(SETTINGS_ID)[self.name].update(data)

    def __getattr__(self, attr, default=_marker):
        res = self.get(attr, default)
        if res is _marker:
            raise AttributeError(attr)
        return res

    def __getitem__(self, name):
        res = self.get(name, _marker)
        if res is _marker:
            raise KeyError(name)
        return res

    def __setitem__(self, name, value):
        data = api.get_cfg_storage(SETTINGS_ID)
        try:
            data[self.name][name] = value
        except KeyError:
            data[self.name] = {}
            data[self.name][name] = value
