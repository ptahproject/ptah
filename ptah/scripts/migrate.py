""" ptah-migrate command """
from __future__ import print_function
import argparse
import textwrap
import alembic.config
import alembic.context
from pyramid.path import AssetResolver

import ptah
import ptah.migrate
from ptah import scripts
from ptah.populate import create_db_schema
from ptah.migrate import upgrade, revision
from ptah.migrate import Context, ScriptDirectory, MIGRATION_ID


def main():
    parser = argparse.ArgumentParser(description="ptah migrate")
    parser.add_argument('config', metavar='config',
                        help='ini config file')

    subparsers = parser.add_subparsers()

    # revision
    subparser = subparsers.add_parser(
        revision.__name__,
        help=revision.__doc__)
    subparser.add_argument('package', metavar='package',
                           help='package name')
    subparser.add_argument("-r", "--revision",
                           type=str, dest='revid',
                           help="Unique revision id")
    subparser.add_argument("-m", "--message",
                           type=str, dest='message',
                           help="Message string to use with 'revision'")
    subparser.set_defaults(cmd='revision')

    # current
    subparser = subparsers.add_parser(
        current.__name__,
        help=current.__doc__)
    subparser.add_argument('package', metavar='package',
                           nargs='*', help='package name')
    subparser.set_defaults(cmd='current')

    # upgrade
    subparser = subparsers.add_parser(
        upgrade.__name__,
        help=upgrade.__doc__)
    subparser.add_argument('package', metavar='package',
                           nargs='*', help='package name')
    subparser.set_defaults(cmd='upgrade')

    # history
    subparser = subparsers.add_parser(
        history.__name__,
        help=history.__doc__)
    subparser.add_argument('package', metavar='package',
                           nargs='*', help='package name')
    subparser.set_defaults(cmd='history')

    # list
    subparser = subparsers.add_parser(
        'list', help='List registered migrations.')
    subparser.set_defaults(cmd='list')

    # parse
    args = parser.parse_args()

    # bootstrap pyramid
    env = scripts.bootstrap(args.config)

    if args.cmd == 'current':
        print ('')
        if not args.package:
            args.package = ptah.get_cfg_storage(MIGRATION_ID).keys()

        for pkg in args.package:
            current(pkg)

    if args.cmd == 'revision':
        if args.revid:
            for ch in ',.;-':
                if ch in args.revid:
                    print ('Revision id contains forbidden characters')
                    ptah.shutdown()
                    return

        revision(args.package, args.revid, args.message)

    if args.cmd == 'upgrade':
        # create db schemas
        create_db_schema(env['registry'], False)

        for pkg in args.package:
            upgrade(pkg)

    if args.cmd == 'history':
        if not args.package:
            args.package = ptah.get_cfg_storage(MIGRATION_ID).keys()

        for pkg in args.package:
            history(pkg)

    if args.cmd == 'list':
        list_migrations(env['registry'])

    ptah.shutdown()


def history(pkg):
    """List changeset scripts in chronological order."""
    script = ptah.migrate.ScriptDirectory(pkg)
    print('')
    print (pkg)
    print ('='*len(pkg))
    for sc in script.walk_revisions():
        print('{0}: {1}'.format(sc.revision, sc.doc))


def current(pkg):
    """Display the current revision."""
    script = ptah.migrate.ScriptDirectory(pkg)

    def display_version(rev):
        rev = script._get_rev(rev)
        if rev is None:
            print ("Package '{0}' rev: None".format(pkg))
        else:
            print ("Package '{0}' rev: {1}{2} {3}".format(
                    pkg, rev.revision, '(head)' if rev.is_head else "",rev.doc))
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


def list_migrations(registry):
    print ('')
    wrpTitle = textwrap.TextWrapper(
        initial_indent='* ',
        subsequent_indent='  ')

    wrpDesc = textwrap.TextWrapper(
        initial_indent='    ',
        subsequent_indent='    ')

    res = []
    for item in registry.introspector.get_category(MIGRATION_ID):
        intr = item['introspectable']
        res.append((intr['package'], intr['title'], intr['path']))

    for pkg, title, path in sorted(res):
        res = AssetResolver(pkg)
        print (wrpTitle.fill('{0}: {1}'.format(pkg, title)))
        print (wrpDesc.fill(path))
        print (wrpDesc.fill(res.resolve(path).abspath()))
        print ('')
