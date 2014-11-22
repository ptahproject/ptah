""" pstatic """
from __future__ import print_function
import os
import shutil
import argparse
from pyramid.paster import bootstrap
from pyramid.path import AssetResolver
from pyramid.config.views import StaticURLInfo

ID_STATIC = 'ptah.amdjs:static'


def main():
    args = StaticCommand.parser.parse_args()
    env = bootstrap(args.config)
    cmd = StaticCommand(args.dst, env['registry'])
    cmd.run()


class StaticCommand(object):

    parser = argparse.ArgumentParser(description="static source management")
    parser.add_argument('config', metavar='config',
                        help='ini config file')
    parser.add_argument('dst', metavar='dst',
                        help='Destination directory')

    ignores = ('~*', '*~', '*.py', '*.pyc', '*.bak', '__pycache__')

    def __init__(self, dst, registry):
        self.dst = dst
        self.registry = registry

    def run(self):
        resolver = AssetResolver()
        dst = os.path.abspath(os.path.join(os.getcwd(), self.dst))

        data = self.registry.get(ID_STATIC)
        if data:
            for name, spec in data.items():
                if name.startswith('/'):
                    name = name[1:]

                dst_path = os.path.join(dst, name)
                if os.path.exists(dst_path):
                    shutil.rmtree(dst_path)

                print('Source: %s' % spec)
                shutil.copytree(
                    resolver.resolve(spec).abspath(), dst_path,
                    ignore=shutil.ignore_patterns(*self.ignores))


class StaticURLInfo(StaticURLInfo):

    def add(self, config, name, spec, **extra):
        data = config.registry.get(ID_STATIC)
        if data is None:
            data = config.registry[ID_STATIC] = {}

        data[name] = spec

        cfg = config.get_settings()
        if cfg['static.rewrite']:
            name = cfg['static.url'] + (
                name[1:] if name.startswith('/') else name)

        super(StaticURLInfo, self).add(config, name, spec, **extra)
