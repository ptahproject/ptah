""" settings api """
import sys, time, logging
import os.path, ConfigParser
import colander
import pyinotify
from ordereddict import OrderedDict
from datetime import datetime, timedelta
from zope import interface
from zope.component import getSiteManager
from zope.component.interfaces import ObjectEvent
from zope.interface.interface import InterfaceClass

try:
    import transaction
except ImportError:
    transaction = None

import api, schema, shutdown
from directives import action, getInfo


CONFIG = None
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


_marker = object()
_settings_initialized = False


def initializeSettings(settings, 
                       config=None, loader=None, watcherFactory=_marker,
                       section=ConfigParser.DEFAULTSECT):
    global _settings_initialized, CONFIG
    if _settings_initialized:
        raise RuntimeError("initializeSettings has been called more than once.")

    log.info('Initializing memphis settings')

    _settings_initialized = True

    CONFIG = config

    if watcherFactory is _marker:
        watcherFactory = iNotifyWatcher

    here = settings.get('here', '')
    if loader is None:
        loader = FileStorage(
            settings.get('settings',''),
            settings.get('defaults', ''),
            here, section, watcherFactory)

    include = settings.get('include', '')
    for f in include.split('\n'):
        f = f.strip()
        if f and os.path.exists(f):
            parser = ConfigParser.SafeConfigParser()
            parser.read(f)
            if section == ConfigParser.DEFAULTSECT or \
                    parser.has_section(section):
                settings.update(parser.items(section, vars={'here': here}))

    Settings.init(loader, settings)
    api.notify(SettingsInitializing(config))
    api.notify(SettingsInitialized(config))   


def registerSettings(name, *nodes, **kw):
    title = kw.get('title', '')
    description = kw.get('description', '')
    validator = kw.get('validator', None)

    iname = name
    for ch in ('.', '-'):
        iname = iname.replace(ch, '_')

    category = InterfaceClass(
        '_group_%s'%iname, (),
        __doc__='Settings group: %s' %name,
        __module__='memphis.config.settings')

    group = Settings.register(name, title, description, category)

    for node in nodes:
        if not isinstance(node, schema.SchemaNode):
            raise RuntimeError(
                "Node '%s' has to be instance of "
                "memphis.config.SchemaNode"%node.name)

        action(
            _registerSettingsImpl,
            name, title, description, validator, node, category,
            __discriminator = ('memphis:registerSettings', node.name, name),
            __info = getInfo(2),
            __frame = sys._getframe(1))

    return group


def _registerSettingsImpl(name, title, description, validator, node, category):
    group = Settings.register(name, title, description, category)

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
            if transaction is not None:
                transaction.get().addAfterCommitHook(self.save)
            
        data = self._changed.setdefault(group, set())
        data.update(attrs)

    def _load(self, rawdata, setdefaults=False, suppressevents=True):
        try:
            rawdata = dict((k.lower(), v) for k, v in rawdata.items())
            data = self.schema.unflatten(rawdata)
        except:
            log.error('Error loading settings')
            return

        try:
            data = self.schema.deserialize(data)
        except colander.Invalid, e:
            errs = e.asdict()
            if setdefaults:
                log.error('Error loading default settings: \n%s'%(
                        '\n'.join('%s: %s'%(k, v) for k, v in errs.items())))
                return

            log.error('Error loading settings, reloading with defaults: \n%s'%(
                    '\n'.join('%s: %s'%(k, v) for k, v in errs.items())))

            defaults = self.schema.flatten(self.schema.serialize())

            for k in errs.keys():
                rawdata.pop(k)
                rawdata[k] = defaults[k]

            data = self.schema.deserialize(self.schema.unflatten(rawdata))

        for name, group in self.items():
            if name in data and data[name]:
                if not suppressevents:
                    modified = data[name] != dict(group)
                    group.update(data[name])
                    if modified:
                        getSiteManager().subscribers(
                            (group, SettingsGroupModified(group)), None)
                else:
                    group.update(data[name])

                if setdefaults:
                    for k, v in data[name].items():
                        if v is not colander.null:
                            group.schema[k].default = v

    def init(self, loader, defaults=None):
        for group in self.values():
            data = dict((node.name, node.default) for node in 
                        group.schema.children 
                        if node.default is not colander.null)
            group.update(data)

        if defaults:
            self._load(defaults, True)

        self.loader = loader
        if loader is None:
            return

        self._load(loader.loadDefaults(), True)
        self._load(loader.load())

    def load(self):
        if self.loader is not None:
            self._load(self.loader.load(), suppressevents=False)

    def save(self, *args):
        if self._changed is not None:
            for grp, attrs in self._changed.items():
                api.notify(SettingsGroupModified(self[grp]))

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

    def register(self, name, title, description, category):
        if name not in self:
            group = Group(name, self, title, description, category)
            self.schema.add(group.schema)
            self[name] = group
        return self[name]


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


class Group(dict):

    def __init__(self, name, settings, title, description, category):
        self.name = name
        self.title = title
        self.description = description
        self.settings = settings
        self.category = category
        self.schema = schema.SchemaNode(
            schema.Mapping(), 
            name=name,
            required=False,
            validator=GroupValidator())

        interface.directlyProvides(self, category)

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


class FileStorage(object):
    """ Simple ConfigParser file storage """

    def __init__(self, cfg, cfgdefaults='', here = '',
                 section=ConfigParser.DEFAULTSECT, watcherFactory=None):
        self.cfg = cfg
        self.cfgdefaults = cfgdefaults
        self.here = here
        self.section = section
        self.watcher = None
        self.watcherFactory = watcherFactory

    def _startWatcher(self, fn):
        if self.watcher is None and self.watcherFactory is not None:
            self.watcher = self.watcherFactory(Settings.load)

        if self.watcher is not None:
            self.watcher.start(fn)

    def close(self):
        if self.watcher is not None:
            self.watcher.stop()

    def load(self):
        if not self.cfg:
            return {}

        if not os.path.exists(self.cfg):
            f = open(self.cfg, 'wb')
            f.write('[%s]\n'%self.section)
            f.close()

        log.info("Loading settings: %s"%self.cfg)
        parser = ConfigParser.SafeConfigParser()
        parser.read(self.cfg)
        self._startWatcher(self.cfg)

        if self.section != ConfigParser.DEFAULTSECT and \
                not parser.has_section(self.section):
            return {}

        return dict(parser.items(self.section, vars={'here': self.here}))

    def loadDefaults(self):
        if os.path.exists(self.cfgdefaults):
            log.info("Loading default settings: %s"%self.cfgdefaults)
            parser = ConfigParser.SafeConfigParser()
            parser.read(self.cfgdefaults)
            data = {}
            if self.section == ConfigParser.DEFAULTSECT or \
                    parser.has_section(self.section):
                data.update(
                    dict(parser.items(self.section, vars={'here': self.here})))

            include = data.get('include', '')
            for f in include.split('\n'):
                f = f.strip()
                if f and os.path.exists(f):
                    parser = ConfigParser.SafeConfigParser()
                    parser.read(f)
                    if self.section == ConfigParser.DEFAULTSECT or \
                            parser.has_section(self.section):
                        data.update(
                            dict(parser.items(
                                    self.section, vars={'here': self.here})))
            return data
        elif not os.path.exists(self.cfgdefaults):
            log.info("Default settings file is not found: %s"%self.cfgdefaults)

        return {}

    def save(self, data):
        if not self.cfg:
            return

        log.info("Saving settings: %s"%self.cfg)

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

        self._startWatcher(self.cfg)


Settings = SettingsImpl()


class iNotifyWatcher(object):

    mask = pyinotify.IN_MODIFY|pyinotify.IN_DELETE_SELF

    started = False
    filename = ''

    def __init__(self, handler):
        self._handler = handler
        self._wd = None
        self._wm = pyinotify.WatchManager()
        self._notifier = pyinotify.ThreadedNotifier(self._wm)

    def _process_ev(self, ev):
        if ev.mask & pyinotify.IN_DELETE_SELF:
            self.stop()
            return

        if ev.mask & pyinotify.IN_MODIFY:
            if CONFIG is not None:
                CONFIG.begin()

            self._handler()

            if CONFIG is not None:
                CONFIG.end()

    def start(self, filename):
        if self.started:
            if self.filename != filename:
                self.stop()
            else:
                return
        
        self._wd = self._wm.add_watch(
            filename, self.mask, self._process_ev, False, False)

        self._notifier.start()
        self.started = True
        self.filename = filename

    def stop(self):
        if self.started:
            try:
                self._notifier.stop()
                if self._wd:
                    self._wm.rm_watch(self._wd.values(), rec=True)
            except:
                pass

            self.filename = ''
            self.started = False


@shutdown.shutdownHandler
def shutdown():
    if Settings.loader is not None:
        Settings.loader.close()


@api.cleanup
def cleanup():
    global Settings, CONFIG, _settings_initialized

    CONFIG = None
    _settings_initialized = False
    
    if Settings.loader is not None:
        Settings.loader.close()
        Settings.loader = None

    # fixme: doenst work but should!
    Settings.clear()
    Settings.schema = schema.SchemaNode(schema.Mapping())

    if '_changed' in Settings.__dict__:
        del Settings._changed
