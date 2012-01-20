import os
import logging
import functools
import pkg_resources
import sqlalchemy as sqla

import alembic.util
import alembic.config
import alembic.context
from alembic.script import ScriptDirectory

import ptah
from ptah import config
from pyramid.path import package_name, AssetResolver

MIGRATION_ID = 'ptah:migrate'


class Version(ptah.get_base()):

    __tablename__ = 'ptah_db_versions'

    package = sqla.Column(sqla.String(128), primary_key=True)
    version_num = sqla.Column(sqla.String(32), nullable=False)


class ScriptDirectory(ScriptDirectory):

    def __init__(self, pkg):
        path = ptah.get_cfg_storage(MIGRATION_ID).get(pkg)
        if path is None:
            raise ValueError("Can't find package.")

        res = AssetResolver(pkg)
        self.dir = res.resolve('ptah:scripts').abspath()
        self.versions = res.resolve(path).abspath()

        if not os.access(self.versions, os.F_OK):
            raise alembic.util.CommandError("Path doesn't exist: %r." % path)


class Context(alembic.context.Context):

    pkg_name = ''

    def _current_rev(self):
        if self.as_sql: # pragma: no cover
            return self._start_from_rev
        else:
            if self._start_from_rev: # pragma: no cover
                raise alembic.util.CommandError(
                    "Can't specify current_rev to context "
                    "when using a database connection")
            Version.__table__.create(checkfirst=True)

        item = ptah.get_session().query(Version.version_num).filter(
            Version.package == self.pkg_name).first()
        return getattr(item, 'version_num', None)

    def _update_current_rev(self, old, new):
        if old == new: # pragma: no cover
            return
        if new is None: # pragma: no cover
            self.impl._exec(Version.__table__.delete().where(
                package=self.pkg_name))
        elif old is None:
            self.impl._exec(
                Version.__table__.insert().
                values(package=self.pkg_name,
                       version_num=sqla.literal_column("'%s'" % new))
                )
        else:
            self.impl._exec(
                Version.__table__.update().
                values(package=self.pkg_name,
                       version_num=sqla.literal_column("'%s'" % new))
                )

    def run_migrations(self, **kw):
        current_rev = rev = False
        log = logging.getLogger('ptah.alembic')
        self.impl.start_migrations()

        for change, prev_rev, rev in self._migrations_fn(self._current_rev()):
            if current_rev is False:
                current_rev = prev_rev
                if self.as_sql and not current_rev: # pragma: no cover
                    Version.__table__.create(checkfirst=True)

            log.info("%s: running %s %s -> %s",
                     self.pkg_name, change.__name__, prev_rev, rev)
            if self.as_sql: # pragma: no cover
                self.impl.static_output(
                    "-- Running %s %s -> %s"%(change.__name__, prev_rev, rev))

            change(**kw)

            if not self.impl.transactional_ddl: # pragma: no cover
                self._update_current_rev(prev_rev, rev)
            prev_rev = rev

        if rev is not False:
            if self.impl.transactional_ddl:
                self._update_current_rev(current_rev, rev)

            if self.as_sql and not rev: # pragma: no cover
                Version.__table___.drop()


def upgrade(pkg, sql=False):
    """Upgrade to a later version."""
    if ':' in pkg:
        pkg, rev = pkg.split(':',1)
    else:
        rev = 'head'

    script = ScriptDirectory(pkg)

    alembic.context.Context = Context
    alembic.context.Context.pkg_name = pkg
    alembic.context._opts(
        alembic.config.Config(''),
        script,
        fn = functools.partial(script.upgrade_from, rev),
        as_sql = sql,
        starting_rev = None,
        destination_rev = rev,
    )

    conn = ptah.get_base().metadata.bind.connect()

    alembic.context.configure(
        connection=conn,
        config=alembic.config.Config(''))

    with alembic.context.begin_transaction():
        alembic.context.run_migrations()


def revision(pkg, rev=None, message=None):
    """Create a new revision file."""
    script = ScriptDirectory(pkg)
    revs = [sc.revision for sc in script.walk_revisions()]

    if not rev:
        rev = alembic.util.rev_id()

    if rev in revs:
        raise KeyError('Revision already exists')

    return script.generate_rev(rev, message)


def ptah_migrate(cfg):
    def action(cfg,):
        for pkg in cfg.get_cfg_storage(MIGRATION_ID).keys():
            upgrade(pkg)

    cfg.action('ptah.ptah_migrate', action, (cfg,), order=999999+1)


def register_migration(pkg, path, title='', force=False):
    """Registers a migration for package.
    Check :ref:`data_migration_chapter` chapter for detailed description.

    :param pkg: Package name
    :param path: String implying a path or `asset specification`
        (e.g. ``ptah:migrations``). Path to directory with migration scripts.
    :param title: Optional human readable title.
    :param force: Force execute migration during bootstrap process

    .. code-block:: python

      import ptah

      ptah.register_migration(
          'ptah', 'ptah:migrations', 'Ptah database migration')

    """
    info = config.DirectiveInfo()
    discr = (MIGRATION_ID, pkg)

    intr = config.Introspectable(MIGRATION_ID, discr, pkg, MIGRATION_ID)
    intr['package'] = pkg
    intr['path'] = path
    intr['title'] = title
    intr['force'] = force

    def _complete(cfg, pkg, path):
        cfg.get_cfg_storage(MIGRATION_ID)[pkg] = path

    info.attach(
        config.Action(
            _complete, (pkg, path),
            discriminator=discr, introspectables=(intr,))
        )


def update_versions(registry):
    packages = []
    for item in registry.introspector.get_category(MIGRATION_ID):
        intr = item['introspectable']
        if not intr['force']:
            packages.append(intr['package'])

    session = ptah.get_session()

    for pkg in packages:
        item = session.query(Version).filter(Version.package==pkg).first()
        if item is not None:
            continue

        script = ScriptDirectory(pkg)
        revs = [sc for sc in script.walk_revisions()]

        # set head as version
        for sc in revs:
            if sc.is_head:
                session.add(Version(package=pkg, version_num=sc.revision))
                break


def check_version(ev):
    """ ApplicationCreated event handler """
    if not Version.__table__.exists():
        return

    versions = dict((v.package, v.version_num)
                    for v in ptah.get_session().query(Version).all())
    packages = ptah.get_cfg_storage(MIGRATION_ID).keys()

    has_steps = False
    log = logging.getLogger('ptah.alembic')

    for pkg in packages:
        version = versions.get(pkg)
        script = ScriptDirectory(pkg)
        for sc in script.walk_revisions():
            if sc.is_head:
                if sc.revision != version:
                    has_steps = True
                    log.error("Package '%s' current revision: '%s', head: '%s'",
                              pkg, version, sc.revision)
                break

    if has_steps:
        config.shutdown()
        log.error("Please run `ptah-migrate` script. Stopping...")
        raise SystemExit(1)
