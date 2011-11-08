""" settings """
import colander
import transaction
import logging, os.path, ConfigParser
from datetime import datetime, timedelta
from collections import OrderedDict
from zope import interface
from zope.interface.interfaces import ObjectEvent
from zope.interface.interface import InterfaceClass

import api, schema, shutdown
from directives import event, subscriber, DirectiveInfo, Action

log = logging.getLogger('ptah.config')


class SettingsInitializing(object):
    """ Settings initializing event """
    event('Settings initializing event')

    config = None

    def __init__(self, config):
        self.config = config


class SettingsInitialized(object):
    """ ptah sends this event when settings initialization is completed. """
    event('Settings initialized event')

    config = None

    def __init__(self, config):
        self.config = config


class SettingsGroupModified(ObjectEvent):
    """ ptah sends this event when settings group is modified. """
    event('Settings group modified event')

    def __init__(self, group, config):
        self.object = group
        self.config = config


_marker = object()

SETTINGS_ID = 'settings'
SETTINGS_OB_ID = 'ptah.config:settings'
SETTINGS_GROUP_ID = 'ptah.config:settings-group'


def get_settings():
    return api.registry.storage.get(SETTINGS_OB_ID)


@subscriber(api.Initialized)
def init_settings(ev):
    settings = Settings()
    ev.registry.storage[SETTINGS_OB_ID] = settings

    # complete settings initialization
    for grp in ev.registry.storage[SETTINGS_GROUP_ID].values():
        settings.register(grp)


def initialize_settings(
    cfg, config=None, loader=None,
    watcherFactory=_marker, section=ConfigParser.DEFAULTSECT):

    settings = api.registry.storage[SETTINGS_OB_ID]
    if settings.initialized:
        raise RuntimeError(
            "initialize_settings has been called more than once.")

    log.info('Initializing ptah settings')

    settings.config = config
    settings.initialized = True

    if watcherFactory is _marker:
        watcherFactory = iNotifyWatcher

    if config is None:
        watcherFactory = None

    here = cfg.get('here', './')
    if loader is None:
        loader = FileStorage(
            settings, cfg.get('settings',''), here, section, watcherFactory)

    include = cfg.get('include', '')
    for f in include.split('\n'):
        f = f.strip()
        if f and os.path.exists(f):
            parser = ConfigParser.SafeConfigParser()
            parser.read(f)
            if section == ConfigParser.DEFAULTSECT or \
                    parser.has_section(section):
                cfg.update(parser.items(section, vars={'here': here}))

    settings.init(loader, cfg)

    try:
        api.notify(SettingsInitializing(config))
        api.notify(SettingsInitialized(config))
    except Exception, e:
        raise api.StopException(e)


def register_settings(name, *nodes, **kw):
    title = kw.get('title', '')
    description = kw.get('description', '')
    validator = kw.get('validator', None)

    iname = name
    for ch in ('.', '-'):
        iname = iname.replace(ch, '_')

    category = InterfaceClass(
        'SettingsGroup:%s'%iname.upper(), (),
        __doc__='Settings group: %s' %name,
        __module__='ptah.config.settings')

    group = Group(name, title, description, category, *nodes)

    if validator is not None:
        if type(validator) not in (list, tuple):
            validator = validator,

        for v in validator:
            group.schema.validator.add(v)

    ac = Action(
        lambda config, group: config.storage[SETTINGS_GROUP_ID].update(
            {group.name: group}),
        (group,),
        discriminator = (SETTINGS_GROUP_ID, name))

    info = DirectiveInfo()
    info.attach(ac)

    return group


class Settings(dict):
    """ settings management system """

    config = None
    loader = None
    initialized = False
    _changed = None

    def __init__(self):
        self.schema = schema.SchemaNode(schema.Mapping())

    def changed(self, group, attrs):
        if not self._changed:
            if self._changed is None:
                self._changed = {}
            transaction.get().addAfterCommitHook(self.save)

        data = self._changed.setdefault(group, set())
        data.update(attrs)

    def _load(self, rawdata, setdefaults=False, suppressevents=True):
        try:
            rawdata = dict((k.lower(), v) for k, v in rawdata.items())
            data = self.schema.unflatten(rawdata)
        except Exception, exc:
            log.error('Error loading settings')
            if setdefaults:
                raise
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
                if setdefaults:
                    for k, v in data[name].items():
                        if v is not colander.null:
                            group.schema[k].default = v

                    group.update(data[name])
                else:
                    if not suppressevents:
                        modified = data[name] != dict(group)
                        group.update(data[name])
                        if modified:
                            api.registry.subscribers(
                                (group,
                                 SettingsGroupModified(group,self.config)),None)
                    else:
                        group.update(data[name])

    def init(self, loader, defaults=None):
        for group in self.values():
            data = {}
            for node in group.schema.children:
                node.default = node._origin_default
                if node.default is not colander.null:
                    data[node.name] = node.default

            group.update(data)

        if defaults:
            self._load(defaults, True)

        self.loader = loader
        if loader is None:
            return

        self._load(loader.load())

    def load(self):
        if self.loader is not None:
            self._load(self.loader.load(), suppressevents=False)

    def save(self, *args):
        if self._changed is not None:
            for grp, attrs in self._changed.items():
                api.notify(SettingsGroupModified(self[grp], self.config))

            self._changed = None

        if self.loader is not None:
            data = self.export()
            if data:
                self.loader.save(data)

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
                    "ptah.config.SchemaNode"%node.name)

            self.schema.add(node)

    def get(self, name, default=None):
        try:
            data = api.registry.storage[SETTINGS_ID][self.name]
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
        api.registry.storage[SETTINGS_ID][self.name].update(data)

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
        if name in self.schema and value != self.get(name):
            get_settings().changed(self.name, (name,))

        api.registry.storage[SETTINGS_ID][self.name][name] = value


class FileStorage(object):
    """ Simple ConfigParser file storage """

    def __init__(self, settings, cfg, here = '',
                 section=ConfigParser.DEFAULTSECT, watcherFactory=None):
        self.cfg = cfg
        self.here = here
        self.section = section
        self.watcher = None
        self.watcherFactory = watcherFactory
        self.settings = settings

    def _startWatcher(self, fn):
        if self.settings and self.watcher is None and \
                self.watcherFactory is not None:
            self.watcher = self.watcherFactory(self.settings.load)

        if self.watcher is not None:
            self.watcher.start(fn)
            shutdown.shutdown_handler(self.watcher.stop)

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


try:
    import pyinotify
except ImportError: # pragma: no cover
    pyinotify = None


class iNotifyWatcher(object):

    if pyinotify:
        mask = pyinotify.IN_MODIFY

    started = False
    filename = ''

    def __init__(self, handler):
        self._handler = handler

    def _process_ev(self, ev):
        if ev.mask & pyinotify.IN_MODIFY:
            self._handler()

    def start(self, filename): # pragma: no cover
        pass

    if pyinotify:
        def start(self, filename):
            if self.started:
                if self.filename != filename: # pragma: no cover
                    self.stop()
                else:
                    return

            wm = pyinotify.WatchManager()
            wm.add_watch(filename, self.mask, self._process_ev, False, False)
            self.notifier = notifier = pyinotify.ThreadedNotifier(wm)
            self.notifier.start()

            self.started = True
            self.filename = filename

    def stop(self):
        if self.started:
            self.filename = ''
            self.started = False

            self.notifier.stop()
            del self.notifier


@shutdown.shutdown_handler
def shutdown_handler():
    settings = get_settings()
    if settings.loader is not None:
        settings.loader.close()
