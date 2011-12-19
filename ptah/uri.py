""" uri resolver """
import uuid
import ptah
from ptah import config

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
    """ Register resolver for given schema. `resolver` is decorator style
    registration.

        :param schema: uri schema

        Resolver interface :py:class:`ptah.interfaces.resolver`

        .. code-block:: python

          import ptah

          @ptah.resolver('custom-schema')
          def my_resolver(uri):
             ....

          # now its possible to resolver 'custom-schema:xxx' uri's
          ptah.resolve('custom-schema:xxx')
    """

    def __init__(self, schema, __depth=1):
        self.info = config.DirectiveInfo(__depth)
        self.discr = (ID_RESOLVER, schema)

        self.intr = config.Introspectable(
            ID_RESOLVER, self.discr, schema, ID_RESOLVER)
        self.intr['schema'] = schema
        self.intr['codeinfo'] = self.info.codeinfo

    def __call__(self, resolver, cfg=None):
        self.intr.title = resolver.__doc__
        self.intr['callable'] = resolver

        self.info.attach(
            config.Action(
                lambda cfg, schema, resolver:
                    cfg.get_cfg_storage(ID_RESOLVER)\
                        .update({schema: resolver}),
                (self.intr['schema'], resolver),
                discriminator=self.discr, introspectables=(self.intr,)),
            cfg)

        return resolver

    @classmethod
    def register(cls, schema, resolver):
        """ Register resolver for given schema

        :param schema: uri schema
        :param resolver: Callable object that accept one parameter.

        Example:

        .. code-block:: python

          import ptah

          def my_resolver(uri):
             ....

          ptah.resolver.register('custom-schema', my_resolver)

          # now its possible to resolver 'custom-schema:xxx' uri's
          ptah.resolve('custom-schema:xxx')

        """
        cls(schema, 2)(resolver)

    @classmethod
    def pyramid(cls, cfg, schema, resolver):
        """ pyramid configurator directive `ptah_uri_resolver`.

        .. code-block:: python

            config = Configurator()
            config.include('ptah')

            def my_resolver(uri):
                ....

            config.ptah_uri_resolver('custom-schema', my_resolver)
        """
        cls(schema, 3)(resolver, cfg)


class UriFactory(object):
    """ Uri Generator

    .. code-block:: python

      uri = UriFactory('cms-content')

      uri()
      'cms-content:f73f3266fa15438e94cca3621a3f2dbc'

    """
    def __init__(self, schema):
        self.schema = schema

    def __call__(self):
        """ Generate new uri using supplied schema """
        return '%s:%s' % (self.schema, uuid.uuid4().hex)
