""" populate data """
import ptah
import logging
import transaction
from zope import interface
from zope.interface import implementer
from pyramid.registry import Registry

POPULATE_DB_SCHEMA = 'ptah-db-schema'


class IPopulateStep(interface.Interface):
    """ Populate step """


class BeforeCreateDbSchema(object):

    def __init__(self, registry):
        self.registry = registry


class Populate(object):

    def __init__(self, registry):
        self.registry = registry

    def list_steps(self, p_steps=None, all=False):
        seen = set()

        steps = dict(
            (name, s) for name, s in
            self.registry.getAdapters((self.registry,), IPopulateStep))

        sorted_steps = []
        def _step(name, step):
            if name in seen:
                return

            seen.add(name)

            for dep in step.requires:
                if dep not in steps:
                    raise RuntimeError(
                        "Can't find populate step '{0}'.".format(dep))
                _step(dep, steps[dep])

            sorted_steps.append((name, step))

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
                elif step.active:
                    _step(name, step)

        return sorted_steps

    def execute(self, p_steps=None):
        steps = self.list_steps(p_steps)

        log = logging.getLogger('ptah')

        for name, step in steps:
            log.info('Executing populate step: %s', name)
            step.execute()

        transaction.commit()


@implementer(IPopulateStep)
class PopulateStep(object):

    title = ''
    requires = ()
    active = True

    def __init__(self, registry):
        self.registry = registry

    def execute(self):
        raise NotImplemented()


@ptah.adapter(Registry, name=POPULATE_DB_SCHEMA)
class CreateDbSchemaStep(PopulateStep):

    title = 'Create db schema'

    def execute(self):
        self.registry.notify(BeforeCreateDbSchema(self.registry))

        skip_tables = ptah.get_settings(CFG_ID_PTAH)['db_skip_tables']

        Base = ptah.get_base()

        log = logging.getLogger('ptah')

        for name, table in Base.metadata.tables.items():
            if name not in skip_tables and not table.exists():
                log.info("Creating db table `%s`.", name)
                table.create()

        transaction.commit()
