""" ptah-migrate command """
from __future__ import print_function
import logging
import argparse
import textwrap

import ptah
from ptah import scripts
from ptah.migrate import upgrade, revision, current
from ptah.migrate import ScriptDirectory, MIGRATION_ID


def main():
    parser = argparse.ArgumentParser(description="ptah migrate")
    parser.add_argument('config', metavar='config',
                        help='ini config file')

    subparsers = parser.add_subparsers()

    # revision
    subparser =  subparsers.add_parser(
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
        for ch in ',.;-':
            if ch in args.revid:
                raise RuntimeError('Revision id contains forbidden characters')

        return revision(args.package, args.revid, args.message)

    if args.cmd == 'upgrade':
        for pkg in args.package:
            return upgrade(pkg)

    if args.cmd == 'history':
        if args.package is not None:
            args.package = ptah.get_cfg_storage(MIGRATION_ID).keys()

        for pkg in args.package:
            history(pkg)


def history(pkg):
    """List changeset scripts in chronological order."""
    script = ScriptDirectory(pkg)
    print('')
    print (pkg)
    print ('='*len(pkg))
    for sc in script.walk_revisions():
        print('{0}: {1}'.format(sc.revision, sc.doc))
