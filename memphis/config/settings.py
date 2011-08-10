""" settings api """
import sys, time, logging
import os.path, ConfigParser
import colander
from ordereddict import OrderedDict
from datetime import datetime, timedelta
from zope import interface, event
from zope.component.interfaces import ObjectEvent

try:
    import transaction
except ImportError:
    transaction = None

import api, schema
from directives import action, getInfo

log = logging.getLogger('memphis.config')


class SettingsInitializing(object):
    """ settings are initializing event """

    config = None

    def __init__(self, config):
        self.config = config


class SettingsInitialized(object):
    """ settings has been initialized event """

    config = None

    def __init__(self, config):
        self.config = config


class SettingsGroupModified(ObjectEvent):
    """ settings group has been modified event """


_settings_initialized = False

def initSettings(settings, 
                 config=None, loader=None, 
                 section=ConfigParser.DEFAULTSECT):
    global _settings_initialized
    if _settings_initialized:
        raise RuntimeError("'initSettings' is been called two times.")

    log.info('Initializing memphis settings api')

    _settings_initialized = True

    here = settings.get('here', '')
    if loader is None:
        loader = FileStorage(
            settings.get('settings',''),
            settings.get('defaultsettings', ''),
            here)
        section = loader.section
    else:
        section = ConfigParser.DEFAULTSECT

    include = settings.get('include', '')
    for f in include.split('\n'):
        f = f.strip()
        if f and os.path.exists(f):
            parser = ConfigParser.SafeConfigParser()
            parser.read(f)
            settings.update(dict(parser.items(section, vars={'here': here})))

    Settings.init(loader, settings)
    event.notify(SettingsInitializing(config))
    event.notify(SettingsInitialized(config))


def registerSettings(name, *nodes, **kw):
    title = kw.get('title', '')
    description = kw.get('description', '')
    validator = kw.get('validator', None)
    category = kw.get('category', None)

    group = Settings.register(name, title, description)

    for node in nodes:
        if not isinstance(node, schema.SchemaNode):
            raise RuntimeError(
                "Node '%s' has to be instance of "
                "memphis.config.SchemaNode"%node.name)

        action(
            registerSettingsImpl,
            name, title, description, validator, category, node, 
            __discriminator = ('memphis:registerSettings', node.name, name),
            __info = getInfo(2),
            __frame = sys._getframe(1))

    return group


def registerSettingsImpl(name, title, description, validator, category, node):
    group = Settings.register(name, title, description)

    if category is not None and not category.providedBy(group):
        interface.directlyProvides(group, category)

    if validator is not None:
        if type(validator) not in (list, tuple):
            validator = validator,

        for v in validator:
            group.schema.validator.add(v)

    group.register(node)


class SettingsImpl(dict):
    """ simple settings management system """

    loader = None
    _changed = None

    def __init__(self):
        self.schema = schema.SchemaNode(schema.Mapping())

    def changed(self, group, attrs):
        if not self._changed:
            if self._changed is None:
                self._changed = {}
            data = self._changed.setdefault(group, set())
            data.update(attrs)
            transaction.get().addAfterCommitHook(self.save)

    def _load(self, rawdata, setdefaults=False):
        rawdata = dict((k.lower(), v) for k, v in rawdata.items())
        data = self.schema.unflatten(rawdata)

        try:
            data = self.schema.deserialize(data)
        except colander.Invalid, e:
            if setdefaults:
                raise

            errs = e.asdict()
            log.error('Error loading settings, reloading with defaults: \n%s'%(
                    '\n'.join('%s: %s'%(k, v) for k, v in errs.items())))

            [rawdata.pop(k) for k in errs.keys()]

            data = self.schema.unflatten(rawdata)
            try:
                data = self.schema.deserialize(data)
            except colander.Invalid, e:
                log.error('Error loading settings')
                return

        for name, group in self.items():
            if name in data and data[name]:
                group.update(data[name])
                if setdefaults:
                    for k, v in data[name].items():
                        if v is not colander.null:
                            group.schema[k].default = v

    def init(self, loader, defaults=None):
        self.loader = loader

        if loader is None:
            return

        if defaults:
            self._load(defaults, True)

        self._load(loader.loadDefaults(), True)
        self._load(loader.load())

    def load(self):
        if self.loader is not None:
            self._load(self.loader.load())

    def save(self, *args):
        if self._changed is not None:
            for grp, attrs in self._changed.items():
                event.notify(self[grp])

            self._changed = None

        if self.loader is not None:
            data = self.export()
            if data:
                self.loader.save(data)

    def export(self, default=False):
        result = {}
        for name, group in self.items():
            data = dict(group)
            result[name] = data

        result = self.schema.serialize(result)

        if not default:
            for prefix, group in self.items():
                schema = group.schema
                for key, val in group.items():
                    if val == schema[key].default:
                        del result[prefix][key]

        return self.schema.flatten(result)

    def register(self, name, title, description):
        if name not in self:
            group = Group(name, self, title, description)
            self.schema.add(group.schema)
            self[name] = group
        return self[name]

    def validate(self, name, value):
        pass

    def validateAll(self, values):
        pass


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
                    error.add(e, node)
                else:
                    error.add(e, node.children.index(e.node))

        if error is not None:
            raise error


_marker = object()

class Group(dict):

    def __init__(self, name, settings, title, description):
        self.__dict__['name'] = name
        self.__dict__['title'] = title
        self.__dict__['description'] = description
        self.__dict__['settings'] = settings
        self.__dict__['schema'] = schema.SchemaNode(
            schema.Mapping(), 
            name=name,
            required=False,
            validator=GroupValidator())

    def register(self, node):
        super(Group, self).__setitem__(node.name, node.default)
        self.schema.add(node)

    def __getattr__(self, attr, default=_marker):
        res = self.get(attr, default)
        if res is _marker:
            raise AttributeError(attr)
        return res

    def __setitem__(self, attr, value):
        if attr in self.schema and value != self[attr]:
            self.settings.changed(self.name, (attr,))
        super(Group, self).__setitem__(attr, value)

    def validate(self, name, value):
        pass

    def validateAll(self, values):
        pass


class FileStorage(object):
    """ Simple ConfigParser file storage """

    def __init__(self, cfg, cfgdefaults='', here = '',
                 section=ConfigParser.DEFAULTSECT, watcher=False):
        self.cfg = cfg
        self.cfgdefaults = cfgdefaults
        self.here = here
        self.section = section

    def load(self):
        if os.path.exists(self.cfg):
            log.info("Loading settings: %s"%self.cfg)
            parser = ConfigParser.SafeConfigParser()
            parser.read(self.cfg)
            return dict(parser.items(self.section, vars={'here': self.here}))

        return {}

    def loadDefaults(self):
        if os.path.exists(self.cfgdefaults):
            log.info("Loading default settings: %s"%self.cfg)
            parser = ConfigParser.SafeConfigParser()
            parser.read(self.cfgdefaults)
            data = dict(parser.items(self.section, vars={'here': self.here}))

            include = data.get('include', '')
            for f in include.split('\n'):
                f = f.strip()
                if f and os.path.exists(f):
                    parser = ConfigParser.SafeConfigParser()
                    parser.read(f)
                    data.update(
                        dict(parser.items(
                                self.section, vars={'here': self.here})))
            return data

        return {}

    def save(self, data):
        if not os.path.exists(self.cfg):
            pass

        log.info("Loading settings: %s"%self.cfg)

        parser = ConfigParser.ConfigParser(dict_type=OrderedDict)
        parser.read(self.cfg)

        if self.section != ConfigParser.DEFAULTSECT and \
                not parser.has_section(self.section):
            parser.add_section(self.section)

        items = data.items()
        items.sort()
        for key, val in items:
            parser.set(self.section, key, val)

        fp = open(self.cfg, 'wb')
        try:
            parser.write(fp)
        finally:
            fp.close()


Settings = SettingsImpl()


class SimpleWatcher(object):

    def __init__(self, settings, timeout=5):
        self.settings = settings
        self.timeout = timedelta(seconds=timeout)
        self.checked = datetime.now()
        self.mtime = time.time()

    def check(self, *args):
        now = datetime.now()
        if (self.checked + self.timeout) < now:
            self.checked = now

            cfg = self.settings.loader.cfg
            if os.path.exists(cfg):
                t = os.path.getmtime(cfg)
                if t > self.mtime:
                    self.mtime = t
                    self.settings.load()
