""" simple template customization """
import os
import logging
import colander
import pyinotify
from zope import interface
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

    title = 'Template related settings',
    )
TEMPLATE._manager = None
TEMPLATE._watcher = None


class TemplatesManager(object):
    
    def __init__(self, directory):
        self.directory = directory

    def load(self):
        try:
            subdirs = os.listdir(self.directory)
        except:
            return

        for dir in subdirs:
            pkg_data = tmpl.registry.get(dir, None)
            if pkg_data is None:
                continue

            path = os.path.join(self.directory, dir)
            if os.path.isdir(path):
                for item in os.listdir(path):
                    if item in pkg_data:
                        pkg_data[item][3].setCustom(
                            tmpl.getRenderer(os.path.join(path, item)))

    def reloadPackage(self, pkg):
        pkg_data = tmpl.registry.get(pkg, None)
        if pkg_data is None:
            return
            
        path = os.path.join(self.directory, pkg)
        if os.path.isdir(path):
            items = dict((f, 1) for f in os.listdir(path))
            for fn, (p,t,d,t) in pkg_data.items():
                if fn in items and t.custom is None:
                    t.setCustom(tmpl.getRenderer(os.path.join(path, fn)))
                else:
                    if t.custom is not None:
                        t.setCustom(None)

    def unload(self):
        for n, pkg_data in tmpl.registry.items():
            for fn, (p,t,d, t) in pkg_data.items():
                if t.custom is not None:
                    t.setCustom(None)


class iNotifyWatcher(object):

    mask = pyinotify.IN_CREATE|pyinotify.IN_DELETE|\
        pyinotify.IN_MOVED_FROM|pyinotify.IN_MOVED_TO

    type = 'inotify'

    def __init__(self, manager):
        self.manager = manager
        self.directory = manager.directory

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

    def stop(self):
        self._notifier.stop()


@config.handler(config.SettingsInitializing)
@config.handler(TEMPLATE.category, config.SettingsGroupModified)
def initialize(*args):
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

        dir = TEMPLATE.custom
        if dir and TEMPLATE._manager is None:
            if not os.path.exists(dir):
                os.mkdir(dir)
            if not os.path.isdir(dir):
                log.warning("Custom path is not directory: %s", dir)
                return

            log.info('Initializing templates customization support')

            TEMPLATE._manager = TemplatesManager(dir)
            TEMPLATE._manager.load()

        if dir and TEMPLATE._watcher is None:
            if TEMPLATE.watcher == 'inotify':
                TEMPLATE._watcher = iNotifyWatcher(TEMPLATE._manager)
                TEMPLATE._watcher.start()
                log.info('Starting custom directory filesystem watcher')
            else:
                log.info('Filesystem watcher is disabled')

        try:
            from chameleon import template
            template.AUTO_RELOAD = TEMPLATE.chameleon_reload
            template.BaseTemplateFile.auto_reload = \
                TEMPLATE.chameleon_reload
        except ImportError:
            pass

    except Exception, e:
        log.warning("Error during view customization initializations: %s", e)


@config.shutdownHandler
def shutdown():
    if TEMPLATE._watcher is not None:
        TEMPLATE._watcher.stop()
        TEMPLATE._watcher = None
