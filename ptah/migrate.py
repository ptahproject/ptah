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

    __tablename__ = 'ptah_db_version'

    package = sqla.Column(sqla.String(128), primary_key=True)
    version_num = sqla.Column(sqla.String(32), nullable=False)


class ScriptDirectory(ScriptDirectory):

    def __init__(self, pkg):
        path = ptah.get_cfg_storage(MIGRATION_ID).get(pkg)
        if path is None:
            raise RuntimeError("Can't find package.")

        res = AssetResolver(pkg)
        self.dir = res.resolve('ptah:scripts').abspath()
        self.versions = res.resolve(path).abspath()

        if not os.access(self.versions, os.F_OK):
            raise alembic.util.CommandError(
                "Path doesn't exist: %r." % self.versions)


class Context(alembic.context.Context):

    pkg_name = ''

    def _current_rev(self):
        if self.as_sql:
            return self._start_from_rev
        else:
            if self._start_from_rev:
                raise alembic.util.CommandError(
                    "Can't specify current_rev to context "
                    "when using a database connection")
            Version.__table__.create(checkfirst=True)

        item = ptah.get_session().query(Version.version_num).filter(
            Version.package == self.pkg_name).first()
        return getattr(item, 'version_num', None)

    def _update_current_rev(self, old, new):
        if old == new:
            return
        if new is None:
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
                if self.as_sql and not current_rev:
                    Version.__table__.create(checkfirst=True)

            log.info("%s: running %s %s -> %s",
                     self.pkg_name, change.__name__, prev_rev, rev)
            if self.as_sql:
                self.impl.static_output(
                    "-- Running %s %s -> %s"%(change.__name__, prev_rev, rev))

            change(**kw)

            if not self.impl.transactional_ddl:
                self._update_current_rev(prev_rev, rev)
            prev_rev = rev

        if rev is not False:
            if self.impl.transactional_ddl:
                self._update_current_rev(current_rev, rev)

            if self.as_sql and not rev:
                Version.__table___.drop()


def register_migration(path, title=''):
    info = config.DirectiveInfo()
    discr = (MIGRATION_ID, path)
    pkg_name = package_name(info.module)

    intr = config.Introspectable(MIGRATION_ID, discr, path, MIGRATION_ID)
    intr['package'] = pkg_name
    intr['path'] = path
    intr['title'] = title

    def _complete(cfg, name, path):
        cfg.get_cfg_storage(MIGRATION_ID)[name] = path

    info.attach(
        config.Action(
            _complete, (pkg_name, path),
            discriminator=discr, introspectables=(intr,))
        )


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

    script.generate_rev(rev, message)


def current(pkg):
    """Display the current revision."""
    script = ScriptDirectory(pkg)
    log = logging.getLogger('ptah.alembic')

    def display_version(rev):
        rev = script._get_rev(rev)
        log.info("Package '{0}' rev: {1}{2} {3}".format(
            pkg, rev.revision, '(head)' if rev.is_head else "", rev.doc))
        return []

    conn = ptah.get_base().metadata.bind.connect()

    alembic.context.Context = Context
    alembic.context.Context.pkg_name = pkg

    alembic.context._opts(
        alembic.config.Config(''),
        script,
        fn = display_version
    )

    alembic.context.configure(
        connection=conn,
        config=alembic.config.Config(''))

    with alembic.context.begin_transaction():
        alembic.context.run_migrations()


def ptah_migrate(cfg):
    def action(cfg,):
        for pkg in cfg.get_cfg_storage(MIGRATION_ID).keys():
            upgrade(pkg)

    cfg.action('ptah.ptah_migrate', action, (cfg,), order=999999+1)
