""" simple template customization """
import os
import logging
import colander
import pyinotify
from chameleon import template as chameleon_template

from memphis import config
from memphis.view import tmpl

log = logging.getLogger('memphis.view')


TEMPLATE = config.registerSettings(
    'template',

    config.SchemaNode(
        colander.Str(),
        name = 'custom',
        default = '',
        title = 'Directory',
        description = 'Filesystem directory with custom templates.'),

    config.SchemaNode(
        colander.Str(),
        name = 'watcher',
        default = 'inotify',
        title = 'Filesystem watcher',
        description = 'Custom filesystem directory watcher.'),

    config.SchemaNode(
        colander.Bool(),
        name = 'chameleon_reload',
        default = False,
        title = 'Auto reload',
        description = 'Enable chameleon templates auto reload.'),

    title = 'Templates settings',
    )
TEMPLATE._manager = None
TEMPLATE._watcher = None


class _ViewLayersManager(object):

    def __init__(self):
        self.layers = {}

    def register(self, layer, discriminator):
        data = self.layers.setdefault(discriminator, [])
        data.append(layer)

    def enabled(self, layer, discriminator):
        data = self.layers.get(discriminator)
        if data:
            return data[-1] == layer
        return False

layersManager = _ViewLayersManager()


class _TemplateLayersManager(object):

    def __init__(self):
        self.layers = {}

    def layer(self, pkg, path):
        abspath, pkgname = tmpl.path(path)
        layer = self.layers.setdefault(pkg, [])
        layer.insert(0, (pkgname, abspath, path))

    def initialize(self, filter=None):
        layers = self.layers

        for pkg, pkg_data in tmpl.registry.items():
            if pkg not in layers:
                continue

            if filter is not None and filter != pkg:
                continue

            for fn, (p,t,d,t) in pkg_data.items():

                for pkgname, abspath, path in layers[pkg]:
                    tpath = os.path.join(abspath, fn)
                    if os.path.isfile(tpath):
                        t.setCustom(tmpl.getRenderer(tpath))
                        break


_Manager = _TemplateLayersManager()

layer = _Manager.layer


class _GlobalLayerManager(object):

    def __init__(self, directory):
        self.directory = directory

    def load(self):
        for dir in os.listdir(self.directory):
            if dir not in tmpl.registry:
                continue

            path = os.path.join(self.directory, dir)

            if os.path.isdir(path):
                pkg_data = tmpl.registry[dir]
                for item in os.listdir(path):
                    if item in pkg_data:
                        pkg_data[item][3].setCustom(
                            tmpl.getRenderer(os.path.join(path, item)))

    def reloadPackage(self, pkg):
        if pkg not in tmpl.registry:
            return

        # unload
        pkg_data = tmpl.registry[pkg]
        for fn, (p,t,d,t,pkg) in pkg_data.items():
            if t.custom is not None:
                t.setCustom(None)

        # re-initialize layers
        _Manager.initialize(pkg)

        # load global custom
        path = os.path.join(self.directory, pkg)

        if os.path.isdir(path):
            pkg_data = tmpl.registry[pkg]
            items = dict((f, 1) for f in os.listdir(path))

            for fn, (p,t,d,t,pkg) in pkg_data.items():
                if fn in items and t.custom is None:
                    t.setCustom(tmpl.getRenderer(os.path.join(path, fn)))
                else:
                    if t.custom is not None:
                        t.setCustom(None)

    def unload(self):
        for n, pkg_data in tmpl.registry.items():
            for fn, (p,t,d,t,pkg) in pkg_data.items():
                if t.custom is not None:
                    t.setCustom(None)


class iNotifyWatcher(object):

    mask = pyinotify.IN_CREATE|pyinotify.IN_DELETE|\
        pyinotify.IN_MOVED_FROM|pyinotify.IN_MOVED_TO

    type = 'inotify'

    def __init__(self, manager):
        self.manager = manager
        self.directory = manager.directory

        self._started = False
        self._wm = pyinotify.WatchManager()
        self._notifier = pyinotify.ThreadedNotifier(self._wm)
        self._wm.add_watch(
            self.manager.directory, 
            self.mask, self._process_ev, True, True)

    def _process_ev(self, ev):
        if ev.dir:
            return

        dir, pkg = os.path.split(ev.path)
        if self.directory == dir:
            self.manager.reloadPackage(pkg)

    def start(self):
        self._notifier.start()
        self._started = True

    def stop(self):
        if self._started:
            self._started = False
            self._notifier.stop()


@config.handler(config.SettingsInitializing)
@config.handler(TEMPLATE.category, config.SettingsGroupModified)
def initialize(*args):
    _Manager.initialize()

    config = args[-1].config
    try:
        dir = TEMPLATE.custom

        if TEMPLATE._manager is not None:
            if TEMPLATE._manager.directory != dir:
                TEMPLATE._manager.unload()
                TEMPLATE._manager = None

        if TEMPLATE._watcher is not None:
            if TEMPLATE._watcher.directory != dir or \
                    TEMPLATE._watcher.type != TEMPLATE.watcher:
                TEMPLATE._watcher.stop()
                TEMPLATE._watcher = None
                log.info('Filesystem watcher has been disabled')

        if dir and TEMPLATE._manager is None:
            if not os.path.exists(dir):
                os.mkdir(dir)
            if not os.path.isdir(dir):
                log.warning("Custom path is not directory: %s", dir)
                return

            log.info('Initializing templates customization support')

            _Manager.initialize()
            TEMPLATE._manager = _GlobalLayerManager(dir)
            TEMPLATE._manager.load()

        if config is not None and dir and \
                TEMPLATE._watcher is None and TEMPLATE._manager is not None:
            if TEMPLATE.watcher == 'inotify':
                TEMPLATE._watcher = iNotifyWatcher(TEMPLATE._manager)
                TEMPLATE._watcher.start()
                log.info('Starting custom directory filesystem watcher')
            else:
                log.info('Filesystem watcher is disabled')

    except Exception, e:
        log.warning("Error during view customization initializations: %s", e)

    chameleon_template.AUTO_RELOAD = TEMPLATE.chameleon_reload
    chameleon_template.BaseTemplateFile.auto_reload = TEMPLATE.chameleon_reload


@config.shutdownHandler
def shutdown():
    if TEMPLATE._watcher is not None:
        TEMPLATE._watcher.stop()
        TEMPLATE._watcher = None


@config.addCleanup
def cleanup():
    _Manager.layers.clear()
    layersManager.layers.clear()
