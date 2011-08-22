""" paste commands """
import textwrap
import StringIO
import ConfigParser
from ordereddict import OrderedDict
from paste.script.command import Command

from memphis import config
from memphis.config import api, directives


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
    group_name = "Memphis"
    parser = Command.standard_parser(verbose=False)
    parser.add_option('-a', '--all', dest='all',
                      action="store_true",
                      help = 'List all registered settings')
    parser.add_option('-l', '--list', dest='section', default='',
                      help = 'List registered settings')
    parser.add_option('-p', '--print', dest='printcfg', 
                      action="store_true",
                      help = 'Print default settings in ConfigParser format')

    def command(self):
        # load all memphis packages
        config.initialize()

        # print defaults
        if self.options.printcfg:
            data = config.Settings.export(True)

            parser = ConfigParser.ConfigParser(dict_type=OrderedDict)
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

        if self.options.all:
            section = ''
        else:
            section = self.options.section

        # print description
        groups = config.Settings.items()
        groups.sort()

        for name, group in groups:
            if section and name != section:
                continue

            print ''
            title = group.title or name

            print grpTitleWrap.fill(title)
            if group.description:
                print grpDescriptionWrap.fill(group.description)

            print
            for node in group.schema:
                default = '<required>' if node.required else node.default
                print nameWrap.fill(
                    '%s.%s: %s (%s: %s)'%(
                        name, node.name, node.title, 
                        node.typ.__class__.__name__, default))

                print nameTitleWrap.fill(node.description)
                print


class IntrospectCommand(Command):
    """ 'introspect' paste command"""

    summary = "Memphis introspection"
    usage = ""
    group_name = "Memphis"
    parser = Command.standard_parser(verbose=False)
    parser.add_option('-l', '--list', dest='list',
                      action="store_true",
                      help = 'List available types of introspection')
    parser.add_option('-p', '--package', dest='package', 
                      help = 'Introspect only specified packages')
    parser.add_option('-t', '--type', dest='type', 
                      help = 'Use specific introspection type')

    def command(self):
        config.initialize()
        packages = api.loadPackages()
        
        # scan packages and load all actions
        seen = set()

        DISCRIMINATORS = directives.DISCRIMINATORS

        for pkg in packages:
            actions = directives.scan(pkg, seen, api.exclude)
            print '================== %s ==============='%pkg

            for action in actions:
                #print action.discriminator, action
                d = DISCRIMINATORS.get(action.discriminator[0])
                if d is not None:
                    d.info(action)
                    
