""" paste commands """
import os.path, shutil, textwrap
from pyramid import testing
from paste.script.command import Command

from ptah import config
from ptah.view import resources


grpTitleWrap = textwrap.TextWrapper(
    initial_indent='* ',
    subsequent_indent='  ',
    width = 80)

nameWrap = textwrap.TextWrapper(
    initial_indent='  - ',
    subsequent_indent='    ', width = 80)

overWrap = textwrap.TextWrapper(
    initial_indent='      ',
    subsequent_indent='      ', width = 80)

nameTitleWrap = textwrap.TextWrapper(
    initial_indent='       ',
    subsequent_indent='       ', width = 80)


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
        pconfig = testing.setUp()
        config.initialize(pconfig, self._include, autoinclude=True)
        registry = config.get_cfg_storage(resources.STATIC_ID)

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
