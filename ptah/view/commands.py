""" paste commands """
import os.path, shutil, textwrap, pkg_resources
from paste.script.command import Command

from ptah import config
from ptah.view import tmpl, resources
from ptah.view.customize import _Manager


grpTitleWrap = textwrap.TextWrapper(
    initial_indent='* ',
    subsequent_indent='  ',
    width = 80)

grpDescriptionWrap = textwrap.TextWrapper(
    initial_indent='    ',
    subsequent_indent='    ', width = 80)


nameWrap = textwrap.TextWrapper(
    initial_indent='  - ',
    subsequent_indent='    ', width = 80)

overWrap = textwrap.TextWrapper(
    initial_indent='      ',
    subsequent_indent='      ', width = 80)

nameTitleWrap = textwrap.TextWrapper(
    initial_indent='       ',
    subsequent_indent='       ', width = 80)

nameDescriptionWrap = textwrap.TextWrapper(
    initial_indent=' * ',
    subsequent_indent='', width = 80)


class TemplatesCommand(Command):
    """ 'templates' paste command"""

    summary = "ptah templates management"
    usage = ""
    group_name = "ptah"
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
        # load all ptah packages
        config.initialize()

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
            for filename, (path,title,desc,_tmpl,pkg_name) in templates:
                if path.lower().startswith(dist.location.lower()):
                    path = '..%s'%path[dist_loc_len:]

                print nameWrap.fill('%s: %s'%(filename, path))
                if title:
                    print nameTitleWrap.fill(title)
                if desc:
                    print nameTitleWrap.fill(desc)

                data = _Manager.layers.get(name)
                if data:
                    for pkgname, abspath, path in data: # pragma: no cover
                        if os.path.exists(os.path.join(abspath, filename)):
                            print overWrap.fill(
                                'overriden by: %s (%s)'%(pkgname, path))
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
            print "Can't find template '%s'"%filename
            return

        path, t, d, _tmpl, pkg = data[filename]

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
            print "Can't find template '%s'"%filename
            return

        if not custom:
            print "Output directory is required, use -o CUSTOMDIR"
            return

        path, t, d, _tmpl, pkg_name = data[filename]

        if not os.path.isdir(custom):
            print "Custom path is not a directory: %s"%custom
            return

        dest = os.path.join(custom, package)
        if not os.path.exists(dest):
            os.makedirs(dest)

        custfile = os.path.join(dest, filename)
        if os.path.exists(custfile):
            if not force:
                print "Custom file '%s' already exists. "\
                    "Use '--force' to override."%filename
                return
            else:
                print 'Overrids:',

        d = open(custfile, 'wb')
        s = open(path, 'rb')
        d.write(s.read())
        d.close()
        s.close()

        print "Template '%s' has been customized.\nPath: %s"%(fn, custfile)


class StaticCommand(Command):
    """ 'static' paste command"""

    summary = "ptah static assets management"
    usage = ""
    group_name = "ptah"
    parser = Command.standard_parser(verbose=False)
    parser.add_option('-l', '--list', dest='section',
                      action="store_true",
                      help = 'List registered static sections')
    parser.add_option('-d', '--dump', dest='dump',
                      help = 'Dump static assets')

    _include = None

    def command(self):
        # load all ptah packages
        config.initialize(self._include)
        registry = config.registry.storage[resources.STATIC_ID]

        if self.options.dump:
            basepath = self.options.dump.strip()
            if not os.path.exists(basepath):
                os.makedirs(basepath)

            if not os.path.isdir(basepath):
                print "Output path is not directory."
                return

            items = registry.items()
            items.sort()
            for name, (path, pkg) in items:
                print "* Coping from '%s' %s"%(pkg, path)

                d = resources.buildTree(path)
                di = d.items()
                di.sort()

                for p, _t in di:
                    bp = os.path.join(basepath, name, p)
                    dest_dir = os.path.split(bp)[0]
                    if not os.path.exists(dest_dir):
                        os.makedirs(dest_dir)

                    forp = '%s/%s'%(pkg, p.split(pkg, 1)[-1])
                    if os.path.exists(bp):
                        print '   skipping ../%s'%forp
                    else:
                        print '   coping ../%s'%forp
                        shutil.copyfile(os.path.join(path, p), bp)

                print

            print basepath
            return

        # list static sections
        if self.options.section:
            items = registry.items()
            items.sort()

            for name, (path, pkg) in items:
                print grpTitleWrap.fill(name)
                print nameWrap.fill('by: %s'%pkg)
                p = path.split(pkg, 1)[-1]
                print nameTitleWrap.fill(' ../%s%s'%(pkg, p))
                print
