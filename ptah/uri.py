""" uri resolver """
import uuid
import ptah
from ptah import config
from ptah.util import tldata

ID_RESOLVER = 'ptah:resolver'


def resolve(uri):
    """ Resolve uri, return resolved object.

    Uri contains two parts, `schema` and `uuid`. `schema` is used for
    resolver selection. `uuid` is resolver specific data. By default
    uuid is a uuid.uuid4 string.
    """
    if not uri:
        return

    try:
        schema, data = uri.split(':', 1)
    except ValueError:
        return None

    try:
        return config.get_cfg_storage(ID_RESOLVER)[schema](uri)
    except KeyError:
        pass

    return None


def extract_uri_schema(uri):
    """ Extract schema of given uri """
    if uri:
        try:
            schema, data = uri.split(':', 1)
            return schema
        except:
            pass

    return None


class resolver(object):
    """ Register resolver for given schema

        :param schema: uri schema
        :param resolver: Callable object that accept one parameter.

        Resolver interface::

        class Resolver(object):

            def __call__(self, uri):
                return content
    """

    def __init__(self, schema, __depth=1):
        self.info = config.DirectiveInfo(__depth)
        self.discr = (ID_RESOLVER, schema)

        self.intr = config.Introspectable(
            ID_RESOLVER, self.discr, schema, ID_RESOLVER)
        self.intr['schema'] = schema
        self.intr['codeinfo'] = self.info.codeinfo

    def __call__(self, resolver):
        self.intr.title = resolver.__doc__
        self.intr['callable'] = resolver

        self.info.attach(
            config.Action(
                lambda cfg, schema, resolver:
                    cfg.get_cfg_storage(ID_RESOLVER)\
                        .update({schema: resolver}),
                (self.intr['schema'], resolver),
                discriminator=self.discr, introspectables=(self.intr,))
            )

        return resolver

    @classmethod
    def register(cls, schema, resolver):
        cls(schema, 2)(resolver)


def pyramid_uri_resolver(config, schema, resolver):
    """ pyramid configurator directive 'ptah_uri_resolver' """
    info = ptah.config.DirectiveInfo()
    discr = (ID_RESOLVER, schema)
    intr = ptah.config.Introspectable(
        ID_RESOLVER,discr,resolver.__doc__,ID_RESOLVER)
    intr['schema'] = schema
    intr['callable'] = resolver
    intr['codeinfo'] = info.codeinfo

    config.action(
        discr,
        lambda config, schema, resolver:
            config.get_cfg_storage(ID_RESOLVER).update({schema:resolver}),
        (config, schema, resolver), introspectables=(intr,))


class UriFactory(object):
    """ Uri Generator

    Example::

       >> uri = UriFactory('cms-content')

       >> uri()
       'cms-content:f73f3266fa15438e94cca3621a3f2dbc'

    """

    def __init__(self, schema):
        self.schema = schema

    def __call__(self):
        """ Generate new uri using supplied schema """
        return '%s:%s' % (self.schema, uuid.uuid4().hex)


class Cache(object):

    def __init__(self):
        self.handlers = {}
        self.default = DefaultHandlerFactory

    def register_handler(self, schema, handler):
        self.handlers[schema] = handler

    def install(self):
        pass

    def uninstall(self):
        pass


class DefaultHandlerFactory(object):

    def __init__(self, schema, resolver):
        self.schema = schema
        self.resolver = resolver

    def __call__(self, uri):
        ob = tldata.get(uri)
        if ob is None:
            ob = self.resolver(uri)
            tldata.set(uri, ob)
        return ob
