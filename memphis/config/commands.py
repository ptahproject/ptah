""" paste commands """
import textwrap
import StringIO
import ConfigParser
from ordereddict import OrderedDict
from paste.script.command import Command

from memphis import config


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


class SettingsCommand(Command):
    """ 'settings' paste command"""

    summary = "Memphis settings management"
    usage = ""
    group_name = "memphis"
    parser = Command.standard_parser(verbose=False)
    parser.add_option('-l', '--list', dest='list', 
                      action="store_true",
                      help = 'List all registered settings')

    parser.add_option('-p', '--print', dest='printcfg', 
                      action="store_true",
                      help = 'Print default settings in ConfigParser format')

    def command(self):
        # load all memphis packages
        config.begin()
        config.loadPackages()
        config.commit()

        # print defaults
        if self.options.printcfg:
            data = config.Settings.export(True)

            parser = ConfigParser.SafeConfigParser(dict_type=OrderedDict)
            items = data.items()
            items.sort()
            for key, val in items:
                parser.set(ConfigParser.DEFAULTSECT, key, val)

            fp = StringIO.StringIO()
            try:
                parser.write(fp)
            finally:
                pass

            print fp.getvalue()
            return

        # print description
        groups = config.Settings.items()
        groups.sort()

        for name, group in groups:
            print ''
            title = group.title or name

            print grpTitleWrap.fill(title)
            if group.description:
                print grpDescriptionWrap.fill(group.description)

            print
            for node in group.schema:
                print nameWrap.fill(
                    '%s.%s: %s (%s: %s)'%(
                        name, node.name, node.title, 
                        node.typ.__class__.__name__, node.default))

                print nameTitleWrap.fill(node.description)
                print
