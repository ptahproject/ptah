""" ptah-settings command """
import argparse
import textwrap

from collections import OrderedDict
from pyramid.compat import configparser, NativeIO

import ptah
from ptah import config, scripts
from ptah.settings import SETTINGS_OB_ID
from ptah.settings import ID_SETTINGS_GROUP


grpTitleWrap = textwrap.TextWrapper(
    initial_indent='* ',
    subsequent_indent='  ')

grpDescriptionWrap = textwrap.TextWrapper(
    initial_indent='    ',
    subsequent_indent='    ')

nameWrap = textwrap.TextWrapper(
    initial_indent='  - ',
    subsequent_indent='    ')

nameTitleWrap = textwrap.TextWrapper(
    initial_indent='       ',
    subsequent_indent='       ')

nameDescriptionWrap = textwrap.TextWrapper(
    initial_indent=' * ',
    subsequent_indent='')


def main(init=True):
    args = SettingsCommand.parser.parse_args()

    # bootstrap pyramid
    if init: # pragma: no cover
        env = scripts.bootstrap(args.config)

    cmd = SettingsCommand(args)
    cmd.run()

    ptah.shutdown()


class SettingsCommand(object):
    """ 'settings' command"""

    parser = argparse.ArgumentParser(description="ptah settings management")
    parser.add_argument('config', metavar='config',
                        help='Config file')
    parser.add_argument('-a', '--all', action="store_true",
                        dest='all',
                        help='List all registered settings')
    parser.add_argument('-l', '--list',
                        dest='section', default='',
                        help='List registered settings')
    parser.add_argument('-p', '--print', action="store_true",
                        dest='printcfg',
                        help='Print default settings in ConfigParser format')

    def __init__(self, args):
        self.config = config
        self.options = args

    def run(self):
        # print defaults
        if self.options.printcfg:
            data = config.get_cfg_storage(SETTINGS_OB_ID).export(True)

            parser = configparser.ConfigParser(dict_type=OrderedDict)
            for key, val in sorted(data.items()):
                parser.set(configparser.DEFAULTSECT,
                           key, val.replace('%', '%%'))

            fp = NativeIO()
            try:
                parser.write(fp)
            finally:
                pass

            print (fp.getvalue())
            return

        if self.options.all:
            section = ''
        else:
            section = self.options.section

        # print description
        groups = sorted(config.get_cfg_storage(ID_SETTINGS_GROUP).items(),
                        key = lambda item: item[1].__title__)

        for name, group in groups:
            if section and name != section:
                continue

            print ('')
            title = group.__title__ or name

            print (grpTitleWrap.fill('{0} ({1})'.format(title, name)))
            if group.__description__:
                print (grpDescriptionWrap.fill(
                    group.__description__))

            print ('')
            for node in group.__fields__.values():
                default = '<required>' if node.required else node.default
                print (nameWrap.fill(
                    ('%s.%s: %s (%s: %s)' % (
                        name, node.name, node.title,
                        node.__class__.__name__, default))))

                print (nameTitleWrap.fill(node.description))
                print ('')
