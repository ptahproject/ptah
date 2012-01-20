""" ptah-manage command """
from __future__ import print_function
import sys
import argparse
import textwrap
from collections import OrderedDict
from pyramid.compat import configparser, NativeIO

import ptah
from ptah import scripts
from ptah.manage.manage import MANAGE_ID


grpTitleWrap = textwrap.TextWrapper(
    initial_indent='* ',
    subsequent_indent='  ')

grpDescriptionWrap = textwrap.TextWrapper(
    initial_indent='    ',
    subsequent_indent='    ')


def main(init=True):
    args = ManageCommand.parser.parse_args()

    # bootstrap pyramid
    if init: # pragma: no cover
        env = scripts.bootstrap(args.config)

    cmd = ManageCommand(args)
    cmd.run()

    ptah.shutdown()


class ManageCommand(object):

    parser = argparse.ArgumentParser(description="ptah manage")
    parser.add_argument('config', metavar='config',
                        help='ini config file')
    parser.add_argument('--list-modules', action="store_true",
                        dest='modules',
                        help='List ptah management modules')

    parser.add_argument('--list-models', action="store_true",
                        dest='models',
                        help='List ptah models')

    def __init__(self, args):
        self.options = args

    def run(self):
        print ('')
        if self.options.modules:
            self.list_modules()
        elif self.options.models:
            self.list_models()
        else:
            self.parser.print_help()

    def list_modules(self):
        cfg = ptah.get_settings(ptah.CFG_ID_PTAH)
        disabled = cfg['disable_modules']

        mods = []
        for name, mod in ptah.get_cfg_storage(MANAGE_ID).items():
            mods.append(
                 {'id': name,
                  'title': mod.title,
                  'description': mod.__doc__,
                  'disabled': name in disabled})

        for mod in sorted(mods, key=lambda item:item['id']):
            print (grpTitleWrap.fill(
                    '{id}: {title} (disabled: {disabled})'.format(**mod)))
            print (grpDescriptionWrap.fill(mod['description']))
            print ('\n')

    def list_models(self):
        cfg = ptah.get_settings(ptah.CFG_ID_PTAH)
        disabled = cfg['disable_models']

        types = []
        for ti in ptah.cms.get_types().values():
            types.append(
                {'name': ti.__uri__,
                 'title': ti.title,
                 'description': ti.description,
                 'disabled': ti.__uri__ in disabled,
                 'cls': ti.cls})

        for ti in sorted(types, key=lambda item:item['name']):
            print (grpTitleWrap.fill(
                    '{name}: {title} (disabled: {disabled})'.format(**ti)))
            if ti['description']:
                print (grpDescriptionWrap.fill(ti['description']))
            print('')

            cls = ti['cls']
            print(grpDescriptionWrap.fill('class: {0}'.format(cls.__name__)))
            print(grpDescriptionWrap.fill('module: {0}'.format(cls.__module__)))
            print('    file: ', sys.modules[cls.__module__].__file__)
            print('\n')
