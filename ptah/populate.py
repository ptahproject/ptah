""" populate data """
import logging
import transaction
from pyramid.request import Request
from pyramid.interfaces import IRequestFactory
from pyramid.threadlocal import manager as threadlocal_manager

import ptah
from ptah import config
from ptah.migrate import update_versions

POPULATE_ID = 'ptah:populate-step'
POPULATE_DB_SCHEMA = 'ptah-db-schema'


class populate(object):
    """Registers a data populate step. Populate steps are used by
    :ref:`data_populate_script` command line tool and by
    :ref:`ptah_populate_dir` pyramid directive for populate system data.

    :param name: Unique step name
    :param title: Human readable title
    :param active: Should this step automaticly executed or not
    :param requires: List of steps that should be executed before this step

    Populate step interface :py:class:`ptah.interfaces.populate_step`.
    Steps are executed after configuration is completed.

    .. code-block:: python

       import ptah

       @ptah.populate('custom-user',
                      title='Create custom user',
                      requires=(ptah.POPULATE_DB_SCHEMA,))
       def create_custom_user(registry):
           # create user

    ``create_custom_user`` executes only after ``ptah.POPULATE_DB_SCHEMA`` step.

    Perpose of inactive steps is for example entering testing data or executing
    custom step.
    """

    def __init__(self, name, title='', active=True, requires=(), __depth=1):
        self.info = config.DirectiveInfo(__depth)
        self.discr = (POPULATE_ID, name)

        self.intr = intr = config.Introspectable(
            POPULATE_ID, self.discr, name, POPULATE_ID)

        intr['name'] = name
        intr['title'] = title
        intr['active'] = active
        intr['requires'] = requires
        intr['codeinfo'] = self.info.codeinfo

    @classmethod
    def pyramid(cls, cfg, name, factory=None,
                title='', active=True, requires=()):
        """ Pyramid `ptah_populate_step` directive:

        .. code-block:: python

          config = Configurator()
          config.include('ptah')

          config.ptah_populate_step('ptah-create-db-schema', factory=..)
        """
        l = populate(name, title, active, requires, 3)(factory, cfg)

    def __call__(self, factory, cfg=None):
        intr = self.intr
        intr['factory'] = factory

        self.info.attach(
            config.Action(
                lambda cfg, name, intr:
                    cfg.get_cfg_storage(POPULATE_ID).update({name: intr}),
                (intr['name'], intr),
                   discriminator=self.discr, introspectables=(intr,)),
            cfg)
        return factory


class Populate(object):

    def __init__(self, registry):
        self.registry = registry

    def list_steps(self, p_steps=None, all=False):
        seen = set()

        steps = dict(
            (name, intr) for name, intr in
            ptah.get_cfg_storage(POPULATE_ID, self.registry).items())

        sorted_steps = []
        def _step(name, step):
            if name in seen:
                return

            seen.add(name)

            for dep in step['requires']:
                if dep not in steps:
                    raise RuntimeError(
                        "Can't find populate step '{0}'.".format(dep))
                _step(dep, steps[dep])

            sorted_steps.append(step)

        if p_steps is not None:
            for name in p_steps:
                if name not in steps:
                    raise RuntimeError(
                        "Can't find populate step '{0}'.".format(name))

                _step(name, steps[name])
        else:
            for name, step in steps.items():
                if all:
                    _step(name, step)
                elif step['active']:
                    _step(name, step)

        return sorted_steps

    def execute(self, p_steps=None, request=None):
        registry = self.registry
        if request is None:
            request_factory = registry.queryUtility(
                IRequestFactory, default=Request)
            request = request_factory.blank('/')
            request.registry = registry

        threadlocals = {'registry':registry, 'request':request}
        threadlocal_manager.push(threadlocals)

        steps = self.list_steps(p_steps)

        log = logging.getLogger(' ptah ')

        for step in steps:
            log.info('Executing populate step: %s', step['name'])
            step['factory'](registry)

        transaction.commit()
        threadlocal_manager.pop()


@populate(POPULATE_DB_SCHEMA, title='Create db schema')
def create_db_schema(registry):
    registry.notify(ptah.events.BeforeCreateDbSchema(registry))

    skip_tables = ptah.get_settings(ptah.CFG_ID_PTAH)['db_skip_tables']

    Base = ptah.get_base()

    log = logging.getLogger('ptah')

    tables = []
    for name, table in Base.metadata.tables.items():
        if name not in skip_tables and not table.exists():
            log.info("Creating db table `%s`.", name)
            tables.append(table)

    if tables:
        Base.metadata.create_all(tables=tables)
        transaction.commit()

    # update db versions
    update_versions(registry)
