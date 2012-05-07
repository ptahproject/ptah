""" jmanifest command """
from __future__ import print_function
import os
import sys
import argparse
import textwrap
import tempfile
import subprocess
from collections import OrderedDict
from pprint import pprint
from pyramid.path import AssetResolver
from pyramid.compat import configparser, NativeIO

import ptah
from ptah import scripts
from ptah.amd import ID_AMD_MODULE
from ptah.mustache import build_hb_bundle, ID_BUNDLE


grpTitleWrap = textwrap.TextWrapper(
    initial_indent='* ',
    subsequent_indent='  ')

grpDescriptionWrap = textwrap.TextWrapper(
    initial_indent='    ',
    subsequent_indent='    ')


def main(init=True):
    args = ManifestCommand.parser.parse_args()

    # bootstrap pyramid
    if init: # pragma: no cover
        env = scripts.bootstrap(args.config)

    cmd = ManifestCommand(args, env['registry'], env['request'])
    cmd.run()

    ptah.shutdown()


class ManifestCommand(object):

    parser = argparse.ArgumentParser(description="jca manifest")
    parser.add_argument('config', metavar='config',
                        help='ini config file')

    parser.add_argument('--list', action="store_true",
                        dest='amd',
                        help='List js bundles')

    parser.add_argument('--debug', action="store_true",
                        dest='debug',
                        help='Generate debug js bundles')

    def __init__(self, args, registry, request):
        self.options = args
        self.registry = registry
        self.request = request

    def run(self):
        self.build_bundles()

        #if self.options.amd:
        #    self.build_bundles()
        #else:
        #    self.parser.print_help()

    def build_bundles(self):
        NODE_PATH = subprocess.check_output(('which', 'node')).strip()
        if not NODE_PATH:
            print ("Can't find nodejs")
            return

        cfg = ptah.get_settings('jca', self.registry)
        if not cfg['specs']:
            print ("Spec files are not specified in .ini file")
            return

        if not cfg['directory']:
            print ("No static directory is specified in .ini file")
            return

        storage = self.registry.get(ID_AMD_MODULE)
        if not storage:
            return

        resolver = AssetResolver()

        specs = OrderedDict()
        for item in cfg['specs']:
            if ':' not in item:
                spec = ''
                specfile = item
            else:
                spec, specfile = item.split(':',1)

            if spec in specs:
                raise ConfigurationError("Spec '%s' already defined."%spec)

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
                    tmod = module[5:]
                    if tmod in tmp_storage:
                        text = build_hb_bundle(tmod, tmp_storage[tmod])
                        processed.append(module)
                        js.append((module, None, text))
                        continue

                    path = storage.get(module)
                    if not path:
                        print ("Can't find module '%s'"%module)
                        return

                    processed.append(module)
                    js.append((module, path, resolver.resolve(path).abspath()))

                _, tpath = tempfile.mkstemp()

                print ('')
                print (grpTitleWrap.fill(jsname))

                f = open(tpath, 'ab')
                for name, path, fpath in js:
                    print(grpDescriptionWrap.fill(
                            '%s: %s'%(name, path or 'templates bundle')))

                    if path is None:
                        f.write(fpath)
                        f.write(';\n')
                    else:
                        with open(fpath, 'rb') as source:
                            f.write(source.read())
                            f.write(';\n')

                f.close()

                path = os.path.join(cfg['directory'] + jsname)
                with open(path, 'wb') as dest:
                    if self.options.debug:
                        dest.write(open(tpath, 'rb').read())
                    else:
                        js = subprocess.check_output(
                            (NODE_PATH,UGLIFY,'-nc',tpath))
                        dest.write(js)

                os.unlink(tpath)

            notprocessed = []
            for name, path in storage.items():
                if name not in processed:
                    notprocessed.append((name, path))

            if spec in ('','main') and notprocessed:
                print ("\n\nList of not processed modules:")
                for name, path, in sorted(notprocessed):
                    print(grpDescriptionWrap.fill('%s: %s'%(name, path)))
