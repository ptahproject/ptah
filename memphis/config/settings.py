""" settings api """
import colander
import transaction
import os.path, ConfigParser
from pprint import pprint


def initSettings(settings, loader=None, section=ConfigParser.DEFAULTSECT):
    if loader is None:
        loader = FileStorage(
            settings.get('settings',''),
            settings.get('defaultsettings', ''),
            settings.get('here', ''))
        
    Settings.init(loader, settings)


def registerSettings(*args, **kw):
    prefix = kw.get('prefix','')
    title = kw.get('title','')
    description = kw.get('description','')

    group = Settings.register(prefix, title, description)

    for node in args:
        group.register(node)

    return group


class SettingsImpl(object):
    """ simple settings management system """

    _loader = None
    _changed = False


    def __init__(self):
        self.groups = {}
        self.schema = colander.SchemaNode(colander.Mapping())

    def changed(self):
        if not self._changed:
            self._changed = True
            transaction.get().addAfterCommitHook(self.save)

    def _load(self, rawdata, setdefaults=False):
        data = self.schema.unflatten(rawdata)
        data = self.schema.deserialize(data)

        for name, group in self.groups.items():
            if name in data and data[name]:
                group.update(data[name])
                if setdefaults:
                    for k, v in data[name].items():
                        group.schema[k].default = v

    def init(self, loader, defaults=None):
        self._loader = loader

        def update():
            loader.onupdate = update

        if defaults:
            self._load(defaults, True)

        self._load(loader.loadDefaults(), True)
        self._load(loader.load())

    def __setitem__(self, attr, value):
        prefix, name = attr.rsplir('.', 1)
        self.groups[prefix][name] = value

    def __getitem__(self, attr):
        prefix, name = attr.rsplir('.', 1)
        return self.groups[prefix][name]

    def save(self, *args):
        self._changed = False
        if self._loader is not None:
            data = self.export()
            if data:
                self._loader.save(data)

    def export(self, default=False):
        result = {}
        for prefix, group in self.groups.items():
            result[prefix] = dict(group)

        result = self.schema.serialize(result)

        for prefix, group in self.groups.items():
            schema = group.schema
            for key, val in group.items():
                if val == schema[key].default:
                    del result[prefix][key]

        return self.schema.flatten(result)

    def register(self, name, title, description):
        if name not in self.groups:
            group = Group(name, self, title, description)
            self.schema.add(group.schema)
            self.groups[name] = group
        return self.groups[name]

    def validate(self, name, value):
        pass

    def validateAll(self, values):
        pass


Settings = SettingsImpl()


class Group(dict):

    def __init__(self, prefix, settings, title, description):
        self.__dict__['prefix'] = prefix
        self.__dict__['title'] = title
        self.__dict__['description'] = title
        self.__dict__['settings'] = settings
        self.__dict__['schema'] = colander.SchemaNode(
            colander.Mapping(), name=prefix, missing=colander.null)

    def register(self, node):
        super(Group, self).__setitem__(node.name, node.default)
        self.schema.add(node)

    def __getattr__(self, attr, default=None):
        return self.get(attr, default)

    def __setitem__(self, attr, value):
        self.settings.changed()
        super(Group, self).__setitem__(attr, value)

    def validate(self, name, value):
        pass

    def validateAll(self, values):
        pass


class Storage(object):
    """ """

    def __init__(self):
        self.onupdate = None

    def load(self):
        raise NotImplemented

    def loadDefault(self):
        raise NotImplemented

    def save(self):
        raise NotImplemented
    
    def update(self):
        raise NotImplemented


class FileStorage(object):
    """ Simple ConfigParser file storage """

    def __init__(self, cfg, cfgdefaults='', here = '',
                 section=ConfigParser.DEFAULTSECT, watcher=False):
        self.cfg = cfg
        self.cfgdefaults = cfgdefaults
        self.here = here
        self.section = section
        self.watcher = False
        self.onupdate = None

    def load(self):
        if os.path.exists(self.cfg):
            parser = ConfigParser.SafeConfigParser()
            parser.read(self.cfg)
            return dict(parser.items(self.section, vars={'here': self.here}))

        return {}

    def loadDefaults(self):
        if os.path.exists(self.cfgdefaults):
            parser = ConfigParser.SafeConfigParser()
            parser.read(self.cfgdefaults)
            return dict(parser.items(self.section, vars={'here': self.here}))

        return {}

    def save(self, data):
        if not os.path.exists(self.cfg):
            pass

        parser = ConfigParser.SafeConfigParser()
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

    def update(self):
        if not callable(self.onupdate):
            return
