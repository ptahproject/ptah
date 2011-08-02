""" settings api """
import colander


def registerSettings(*args, **kw):
    prefix = kw.get('prefix','')
    group = Settings.register(prefix)

    for node in args:
        group.register(node)


class SettingsImpl(object):
    """
    >>> Settings[prefix.name] = 'blah'

    >>> val = Settings[prefix.name]

    >>> group = Settings.group[prefix]
    >>> group[name] = 'blah'
    >>> val = group[name]
    """

    def __init__(self):
        self.groups = {}
        self.schema = colander.SchemaNode(colander.Mapping())

    def init(self, loader):
        self.loader = loader
        
        def update():
            loader.onupdate = update

    def __setitem__(self, attr, value):
        prefix, name = attr.rsplir('.', 1)
        self.groups[prefix][name] = value

    def __getitem__(self, attr):
        prefix, name = attr.rsplir('.', 1)
        return self.groups[prefix][name]

    def export(self):
        result = {}
        for prefix, group in self.groups.items():
            result[prefix] = dict(group)
        return result

    def register(self, name):
        if name not in self.groups:
            group = Group(name, self)
            self.schema.add(group.schema)
            self.groups[name] = group
        return self.groups[name]

    def validate(self, name, value):
        pass

    def validateAll(self, values):
        pass


Settings = SettingsImpl()


class Group(dict):

    def __init__(self, prefix, settings):
        self.__dict__['prefix'] = prefix
        self.__dict__['settings'] = settings
        self.__dict__['schema'] = colander.SchemaNode(
            colander.Mapping(), name=prefix)

    def register(self, node):
        super(Group, self).__setitem__(node.name, node.default)
        self.schema.add(node)

    def __setattr__(self, attr, value):
        self[attr] = value

    def __getattr__(self, attr):
        pass

    def __setitem__(self, attr, value):
        self.settings.changed = True
        super(Group, self).__setitem__(attr, value)

    def validate(self, name, value):
        pass

    def validateAll(self, values):
        pass


class Storage(object):

    def __init__(self):
        self.onupdate = None

    def load(self):
        pass

    def save(self):
        pass
