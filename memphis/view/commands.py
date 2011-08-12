""" paste commands """
import os.path
import textwrap
import pkg_resources
from paste.script.command import Command

from memphis import config
from memphis.view import tmpl


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


class TemplatesCommand(Command):
    """ 'templates' paste command"""

    summary = "Memphis templates management"
    usage = ""
    group_name = "Memphis"
    parser = Command.standard_parser(verbose=False)
    parser.add_option('-a', '--all', dest='all',
                      action="store_true",
                      help = 'List all registered templaes')
    parser.add_option('-l', '--list', dest='section', default='',
                      help = 'List registered templates')
    parser.add_option('-p', '--print', dest='filename',
                      metavar="PACKAGE:FILE",
                      help = 'Print template')
    parser.add_option('-c', '--customize', dest='custfile',
                      metavar="PACKAGE:FILE",
                      help = 'Customize template')
    parser.add_option('-o', '--output', dest='customdir',
                      help = 'Directory for custom templates.')
    parser.add_option('-f', '--force', dest="force",
                      action="store_true", default=False,
                      help = 'Force override custom template.')

    def command(self):
        # load all memphis packages
        config.begin()
        config.loadPackages()
        config.commit()
        
        if self.options.filename:
            self.print_template(self.options.filename)
            return

        if self.options.custfile:
            self.customize_template(self.options.custfile, 
                                    self.options.customdir,
                                    self.options.force)
            return

        # print description
        if self.options.all:
            section = ''
        else:
            section = self.options.section

        items = tmpl.registry.items()
        items.sort()
        for name, data in items:
            if section and name != section:
                continue

            dist = None
            pkg_name = name
            while 1:
                try:
                    dist = pkg_resources.get_distribution(pkg_name)
                    if dist is not None:
                        break
                except pkg_resources.DistributionNotFound:
                    if '.' not in pkg_name:
                        break
                    pkg_name = pkg_name.rsplit('.',1)[0]
            
            if dist is None:
                continue

            print ''
            title = name

            print grpTitleWrap.fill(title)
            #if group.description:
            #    print grpDescriptionWrap.fill(group.description)

            dist_loc_len = len(dist.location)

            print
            templates = data.items()
            templates.sort()
            for filename, (path,title,desc,_tmpl) in templates:
                if path.startswith(dist.location):
                    path = '..%s'%path[dist_loc_len:]

                print nameWrap.fill('%s: %s'%(filename, path))
                if title:
                    print nameTitleWrap.fill(title)
                if desc:
                    print nameTitleWrap.fill(desc)
                print

    def print_template(self, filename):
        if ':' not in filename:
            print "Template path format is wrong, it should be PACKAGE:FILENAME"
            return

        package, filename = filename.split(':')
        if package not in tmpl.registry:
            print "Can't find package '%s'"%package
            return

        data = tmpl.registry[package]
        if filename not in data:
            print "Can't find template '%s'"%package
            return

        path, t, d, _tmpl = data[filename]
        
        if t:
            print t
        if d:
            print d
        print 'Package:  %s'%package
        print 'Template: %s'%filename
        print '='*80

        f = open(path, 'rb')
        print f.read()
        f.close()

    def customize_template(self, fn, custom, force=False):
        if ':' not in fn:
            print "Template path format is wrong, it should be PACKAGE:FILENAME"
            return

        package, filename = fn.split(':')
        if package not in tmpl.registry:
            print "Can't find package '%s'"%package
            return

        data = tmpl.registry[package]
        if filename not in data:
            print "Can't find template '%s'"%package
            return

        if not custom:
            print "-o CUSTOMDIR is requird"
            return

        path, t, d, _tmpl = data[filename]

        dest = os.path.join(custom, package)
        if not os.path.exists(dest):
            os.makedirs(dest)

        if not os.path.isdir(dest):
            print "Custom directory is not a directory: %s"%dest
            return

        custfile = os.path.join(dest, filename)
        if os.path.exists(custfile) and not force:
            print "Custom template '%s' already exists. "\
                "Use '--force' to override."%filename
            return

        d = open(custfile, 'wb')
        s = open(path, 'rb')
        d.write(s.read())
        d.close()
        s.close()

        print "Template '%s' has been customized.\nPath: %s"%(fn, custfile)
