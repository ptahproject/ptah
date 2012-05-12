""" jmanifest command """
from __future__ import print_function
import os
import sys
import argparse
import textwrap
import tempfile
from collections import OrderedDict
from pprint import pprint
from pyramid.path import AssetResolver
from pyramid.compat import configparser, NativeIO, bytes_
from pyramid.threadlocal import get_current_registry

import ptah
from ptah import scripts
from ptah.amd import ID_AMD_MODULE
from ptah.mustache import build_hb_bundle, check_output, ID_BUNDLE


grpTitleWrap = textwrap.TextWrapper(
    initial_indent='* ',
    subsequent_indent='  ')

grpDescriptionWrap = textwrap.TextWrapper(
    initial_indent='    ',
    subsequent_indent='    ')


def main(init=True):
    args = AmdjsCommand.parser.parse_args()

    # bootstrap pyramid
    if init: # pragma: no cover
        env = scripts.bootstrap(args.config)

    cmd = AmdjsCommand(args)
    cmd.run()

    ptah.shutdown()


class AmdjsCommand(object):

    parser = argparse.ArgumentParser(description="amdjs management")
    parser.add_argument('config', metavar='config',
                        help='ini config file')

    parser.add_argument('-b', action="store_true",
                        dest='build',
                        help='Build js bundles')

    parser.add_argument('-m', action="store_true",
                        dest='amd_mods',
                        help='List amd modules')

    parser.add_argument('--no-min', action="store_true",
                        dest='nomin',
                        help='Do not minimize js bundles')

    def __init__(self, args):
        self.options = args
        self.registry = get_current_registry()

    def run(self):
        if self.options.build:
            self.build_bundles()
        elif self.options.amd_mods:
            self.list_amd_mods()
        else:
            self.parser.print_help()

    def list_amd_mods(self):
        print()
        for name, intr in sorted(self.registry.get(ID_AMD_MODULE).items()):
            print(grpTitleWrap.fill('%s: %s'%(name, intr['path'])))
            desc = grpDescriptionWrap.fill(intr['description'])
            print (desc)
            if desc:
                print()

    def build_bundles(self):
        cfg = ptah.get_settings(ptah.CFG_ID_PTAH, self.registry)

        NODE_PATH = cfg['nodejs-path']
        if not NODE_PATH:
            NODE_PATH = check_output(('which', 'node')).strip()

        if not NODE_PATH: # pragma: no cover
            print ("Can't find nodejs")
            return

        if not cfg['amd-spec']:
            print ("Spec files are not specified in .ini file")
            return

        if not cfg['amd-dir']:
            print ("Destination directory is not specified in .ini file")
            return

        storage = self.registry.get(ID_AMD_MODULE)
        if not storage: # pragma: no cover
            return

        resolver = AssetResolver()

        specs = OrderedDict()
        for item in cfg['amd-spec']:
            spec, specfile = item.split(':',1)
            specs[spec] = specfile

        UGLIFY = resolver.resolve(
            'ptah:node_modules/uglify-js/bin/uglifyjs').abspath()

        for spec, specfile in specs.items():
            print("\n\nProcessing: %s (%s)"%(spec, specfile))
            f = resolver.resolve(specfile).abspath()
            parser = configparser.SafeConfigParser()
            parser.read(f)

            bundles = []
            processed = []

            for section in parser.sections():
                if section.endswith('.js'):
                    items = dict(parser.items(section))
                    url = items.get('url', '')
                    modules = items.get('modules', '')
                    if not modules:
                        continue

                    modules = [s for s in [s.strip() for s in modules.split()]
                               if not s.startswith('#') and s]
                    bundles.append((section, url, modules))

            tmp_storage = self.registry.get(ID_BUNDLE)

            for jsname, url, modules in bundles:
                js = []
                for module in modules:
                    if module in tmp_storage:
                        text = build_hb_bundle(
                            module, tmp_storage[module], self.registry)
                        processed.append(module)
                        js.append((module, None, text))
                        continue

                    intr = storage.get(module)
                    if not intr: # pragma: no cover
                        print ("Can't find module '%s'"%module)
                        return

                    processed.append(module)
                    js.append((module, intr['path'],
                               resolver.resolve(intr['path']).abspath()))

                _, tpath = tempfile.mkstemp()

                print ('')
                print (grpTitleWrap.fill(jsname))

                f = open(tpath, 'ab')
                for name, path, fpath in js:
                    print(grpDescriptionWrap.fill(
                            '%s: %s'%(name, path or 'templates bundle')))

                    if path is None:
                        f.write(bytes_(fpath, 'utf8'))
                        f.write(bytes_(';\n', 'utf8'))
                    else:
                        with open(fpath, 'rb') as source:
                            f.write(source.read())
                            f.write(bytes_(';\n', 'utf8'))

                f.close()

                path = os.path.join(cfg['amd-dir'], jsname)
                print ('write to:', path)
                with open(path, 'wb') as dest:
                    if self.options.nomin:
                        dest.write(open(tpath, 'rb').read())
                    else:
                        js = check_output((NODE_PATH,UGLIFY,'-nc',tpath))
                        dest.write(js)

                os.unlink(tpath)

            notprocessed = []
            for name, path in storage.items():
                if name not in processed:
                    notprocessed.append((name, path))

            if spec in ('','main') and notprocessed:
                print ("\n\nList of not processed modules:")
                for name, intr, in sorted(notprocessed):
                    print(grpDescriptionWrap.fill('%s: %s'%(name,intr['path'])))
