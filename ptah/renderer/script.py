""" ptah.renderer command """
from __future__ import print_function
import os
import argparse
import textwrap
import shutil
from pyramid.path import AssetResolver
from pyramid.paster import bootstrap
from pyramid.interfaces import IRendererFactory

from .layer import ID_LAYER


grpTitleWrap = textwrap.TextWrapper(
    initial_indent='* ',
    subsequent_indent='  ')

grpDescriptionWrap = textwrap.TextWrapper(
    initial_indent='    ',
    subsequent_indent='    ')

grpThirdLevelWrap = textwrap.TextWrapper(
    initial_indent='      ',
    subsequent_indent='      ', width=250)


def main():
    args = LayersCommand.parser.parse_args()
    cmd = LayersCommand(args)
    cmd.run()


class LayersCommand(object):

    parser = argparse.ArgumentParser(description="ptah.renderer management")
    parser.add_argument('config', metavar='config',
                        help='ini config file')

    # layers/templates
    parser.add_argument('-l', action="store", nargs="*",
                        dest='layers', help='List layers')

    parser.add_argument('-lt', action="store", nargs="*",
                        dest='templates', help='List templates')

    parser.add_argument('-c', action="store", nargs=2,
                        dest='customize', help='Customize template')


    def __init__(self, args):
        self.options = args
        self.env = bootstrap(args.config)
        self.registry = self.env['registry']
        self.resolver = AssetResolver()

    def run(self):
        if self.options.layers is not None:
            self.list_layers()
        elif self.options.templates is not None:
            self.list_templates()
        elif self.options.customize is not None:
            self.customize()
        else:
            self.parser.print_help()

    def customize(self):
        storage = self.registry.get(ID_LAYER, {})

        tmpl, dest = self.options.customize

        # find template
        if ':' not in tmpl:
            print ('Template format is wrong.')
            return

        layer, tname = tmpl.split(':', 1)
        if tname.endswith('.lt'):
            tname = tname[:-3]

        if layer not in storage:
            print ('Layer "%s" could not be found.'%layer)
            return

        extensions = [name for name, factory in
                      self.registry.getUtilitiesFor(IRendererFactory)
                      if name.startswith('.')]

        template_path = None

        layer_data = storage[layer]
        for intr in layer_data:
            for ext in extensions:
                fname = os.path.join(intr['path'], '%s%s'%(tname, ext))
                if os.path.exists(fname):
                    template_path = fname
                    break

        if template_path is None:
            print ('Template "%s" could not be found.'%tmpl)
            return

        # get destination directory
        dest_path = os.path.abspath(dest)
        if not os.path.isdir(dest_path):
            dest_path = self.resolver.resolve(dest).abspath()

        if not os.path.isdir(dest_path):
            print ('Destination directory is not found.')
            return

        shutil.copy(template_path, dest_path)

        print ('Source: "%s"'%template_path)
        print ('Destination: "%s"'%
               os.path.join(dest_path, os.path.split(template_path)[-1]))

    def list_layers(self):
        storage = self.registry.get(ID_LAYER)
        if not storage:
            print ('No layers are found.')
            return

        storage = sorted(storage.items())
        filter = [s.strip().split(':',1)[0] for s in self.options.layers]

        for name, layers in storage:
            if filter and name not in filter:
                continue

            print(grpTitleWrap.fill('Layer: %s'%name))

            for layer in layers:
                print(grpDescriptionWrap.fill('name: %s'%layer['name']))
                print(grpDescriptionWrap.fill('path: %s'%layer['asset']))

            print()

    def list_templates(self):
        storage = self.registry.get(ID_LAYER)
        if not storage:
            print ('No layers are found.')
            return

        print()

        storage = sorted(storage.items())
        f_layers = [s.strip().split(':',1)[0] for s in self.options.templates]

        factories = dict(
            (name, factory) for name, factory in
            self.registry.getUtilitiesFor(IRendererFactory)
            if name.startswith('.'))

        for name, layers in storage:
            if f_layers and name not in f_layers:
                continue

            print(grpTitleWrap.fill('Layer: %s'%name))

            tmpls = {}
            for layer in layers:
                if os.path.isdir(layer['path']):
                    for name in os.listdir(layer['path']):
                        if '.' in name:
                            rname, rtype = os.path.splitext(name)
                            key = (layer['asset'], rname)
                            if rtype in factories and key not in tmpls:
                                tmpls[key] = rtype

                curr_asset = None
                for (asset, rname), rtype in sorted(tmpls.items()):
                    if curr_asset != asset:
                        curr_asset = asset
                        print('')
                        print(grpDescriptionWrap.fill(asset))

                    if rname in layer['filters']:
                        f = layer['filters'][rname]
                        sinfo = ('%s.py: %s'%(
                            f.__module__.replace('.', '/'), f.__name__))
                        print(grpThirdLevelWrap.fill('%s: %s (%s)'%(
                            rname, rtype, sinfo)))
                    else:
                        print(grpThirdLevelWrap.fill('%s: %s'%(rname, rtype)))

            print()
