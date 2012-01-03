from __future__ import print_function
import sys
import argparse
import logging
import textwrap

import ptah
from ptah import scripts, populate as populate_mod

log = logging.getLogger('ptah')


def main():
    parser = argparse.ArgumentParser(description="ptah populate")
    parser.add_argument('config', metavar='config',
                        help='ini config file')
    parser.add_argument('step', metavar='step', nargs='*',
                        help='list of populate steps')
    parser.add_argument('-l', action="store_true", dest='list',
                        help='list of registered populate steps')
    parser.add_argument('-a', action="store_true", dest='all',
                        help='execute all active populate steps')
    args = parser.parse_args()

    env = scripts.bootstrap(args.config)

    populate = ptah.Populate(env['registry'])

    if args.list:
        titleWrap = textwrap.TextWrapper(
            initial_indent='* ',
            subsequent_indent='  ')

        descWrap = textwrap.TextWrapper(
            initial_indent='    ',
            subsequent_indent='    ')

        print('')

        for name, step in populate.list_steps(all=True):
            print(titleWrap.fill('{0}: {1} ({2})'.format(
                name, step.title, 'active' if step.active else 'inactive')))
            if step.__doc__:
                print(descWrap.fill(step.__doc__))

            print('')
    elif args.all:
        populate.execute()
    elif args.step:
        populate.execute(args.step)
    else:
        parser.print_help()
