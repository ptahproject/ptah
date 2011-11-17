""" custom SchemaNode, Mapping, Sequence class """
import colander


class Required(colander.Invalid):

    def __init__(self, node, msg='Required', value=None):
        super(Required, self).__init__(node, msg, value)


class RequiredWithDependency(object):
    """ Validator which fails only if other key is set. """

    def __init__(self, key, depkey,
                 depval=colander.required, default=colander.required):
        self.key = key
        self.depkey = depkey
        self.depval = depval
        self.default = default

    def __call__(self, node, appstruct):
        if appstruct:
            val = appstruct.get(self.depkey)

            hasVal = False
            if self.depval is not colander.required:
                hasVal = val == self.depval
            else:
                if val:
                    hasVal = True

            if hasVal:
                node = node[self.key]
                default = self.default
                if default is colander.required:
                    default = node.default

                val = appstruct.get(self.key, default)
                if val == default:
                    raise Required(node)


class Mapping(colander.Mapping):

    def flatten(self, node, appstruct, prefix='', listitem=False):
        result = {}
        selfprefix = ''
        if listitem:
            selfprefix = prefix
        elif node.name:
            selfprefix = '%s%s.' % (prefix, node.name)

        for subnode in node.children:
            name = subnode.name
            if name in appstruct:
                substruct = appstruct[name]
                result.update(subnode.typ.flatten(
                        subnode, substruct, prefix=selfprefix))
        return result

    def unflatten(self, node, paths, fstruct):
        return _unflatten_mapping(node, paths, fstruct)


class Sequence(colander.Sequence):

    def flatten(self, node, appstruct, prefix='', listitem=False):
        result = {}
        selfprefix = ''
        if listitem:
            selfprefix = prefix
        elif node.name:
            selfprefix = '%s%s.' % (prefix, node.name)

        childnode = node.children[0]

        for num, subval in enumerate(appstruct):
            subname = '%s%s' % (selfprefix, num)
            subprefix = subname
            result.update(childnode.typ.flatten(
                    childnode, subval, prefix=subprefix, listitem=True))

        return result


Seq = Sequence


class String(colander.Str):

    def __init__(self, encoding='utf-8'):
        self.encoding = encoding


Str = String
colander.Str = String
colander.String = String


class SchemaNode(colander.SchemaNode):

    def __init__(self, typ, *children, **kw):
        super(SchemaNode, self).__init__(typ, *children, **kw)

        self.required = kw.pop('required', self.default is colander.null)
        self._origin_default = self.default

    def __get_required(self):
        return self.__dict__.get('required')

    def __set_required(self, val):
        self.__dict__['required'] = val

    required = property(__get_required, __set_required)

    def deserialize(self, cstruct=colander.null):
        appstruct = self.typ.deserialize(self, cstruct)
        if appstruct is colander.null:
            appstruct = self.default

        if self.preparer is not None:
            appstruct = self.preparer(appstruct)

        if self.required and appstruct == self.default:
            raise Required(self)

        if self.validator is not None:
            self.validator(self, appstruct)

        return appstruct


def _unflatten_mapping(node, paths, fstruct,
                       get_child=None, rewrite_subpath=None):
    if get_child is None:
        get_child = node.__getitem__
    if rewrite_subpath is None:
        def rewrite_subpath(subpath):
            return subpath
    node_name = node.name
    if node_name:
        prefix = node_name + '.'
    else:
        prefix = ''
    prefix_len = len(prefix)
    appstruct = {}
    subfstruct = {}
    subpaths = []
    curname = None
    for path in paths:
        if path == node_name or (prefix and not path.startswith(prefix)):
            # flattened structs contain non-leaf nodes which are ignored
            # during unflattening.
            continue  # pragma: no cover
        assert path.startswith(prefix), "Bad node: %s" % path
        subpath = path[prefix_len:]
        if '.' in subpath:
            name = subpath[:subpath.index('.')]
        else:
            name = subpath
        if curname is None:
            curname = name
        elif name != curname:
            try:
                subnode = get_child(curname)
            except:
                subfstruct = {}
                subpaths = []
                curname = name
            else:
                appstruct[curname] = subnode.typ.unflatten(
                    subnode, subpaths, subfstruct)
                subfstruct = {}
                subpaths = []
                curname = name

        subpath = rewrite_subpath(subpath)
        subfstruct[subpath] = fstruct[path]
        subpaths.append(subpath)

    if curname is not None:
        try:
            subnode = get_child(curname)
        except KeyError:
            pass
        else:
            appstruct[curname] = subnode.typ.unflatten(
                subnode, subpaths, subfstruct)

    return appstruct
