""" ptah-alembic command """
from __future__ import print_function
import logging
import argparse
import textwrap

import alembic.util
import alembic.config
import alembic.context

import ptah
from ptah import scripts
from ptah.ptahalembic import \
     MIGRATION_ID, upgrade, Version, Context, ScriptDirectory


def main():
    parser = argparse.ArgumentParser(description="ptah alembic")
    parser.add_argument('config', metavar='config',
                        help='ini config file')

    subparsers = parser.add_subparsers()

    # revision
    subparser =  subparsers.add_parser(
        revision.__name__,
        help=revision.__doc__)
    subparser.add_argument('package', metavar='package',
                           help='package name')
    subparser.add_argument("-m", "--message",
                           type=str, dest='message',
                           help="Message string to use with 'revision'")
    subparser.set_defaults(cmd='revision')

    # current
    subparser =  subparsers.add_parser(
        current.__name__,
        help=current.__doc__)
    subparser.add_argument('package', metavar='package',
                           nargs='*', help='package name')
    subparser.set_defaults(cmd='current')

    # upgrade
    subparser =  subparsers.add_parser(
        upgrade.__name__,
        help=upgrade.__doc__)
    subparser.add_argument('package', metavar='package',
                           nargs='*', help='package name')
    subparser.set_defaults(cmd='upgrade')

    # history
    subparser =  subparsers.add_parser(
        history.__name__,
        help=history.__doc__)
    subparser.add_argument('package', metavar='package',
                           nargs='*', help='package name')
    subparser.set_defaults(cmd='history')

    # parse
    args = parser.parse_args()

    # bootstrap pyramid
    env = scripts.bootstrap(args.config)

    if args.cmd == 'current':
        if args.package is not None:
            args.package = ptah.get_cfg_storage(MIGRATION_ID).keys()

        for pkg in args.package:
            current(pkg)

    if args.cmd == 'revision':
        return revision(args.package, args.message)

    if args.cmd == 'upgrade':
        for pkg in args.package:
            return upgrade(pkg)

    if args.cmd == 'history':
        if args.package is not None:
            args.package = ptah.get_cfg_storage(MIGRATION_ID).keys()

        for pkg in args.package:
            history(pkg)


def revision(pkg, message=None):
    """Create a new revision file."""
    script = ScriptDirectory(pkg)
    script.generate_rev(alembic.util.rev_id(), message)


def history(pkg):
    """List changeset scripts in chronological order."""
    script = ScriptDirectory(pkg)
    print('')
    print (pkg)
    print ('='*len(pkg))
    for sc in script.walk_revisions():
        print('{0}: {1}'.format(sc.revision, sc.doc))


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
