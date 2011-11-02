""" addon system """
import pkg_resources
from ptah  import config, view, manage
from ptah.config import directives
from ptah.manage.manage import INTROSPECT_ID

from core import ADDONS


class AddonsModule(manage.PtahModule):
    """Add-ons management"""

    title = 'Add-ons'
    manage.module('addons')

    def __getitem__(self, key):
        dist = ADDONS.get(key)
        if dist is not None:
            return Addon(dist, self)

        raise KeyError(key)


class Addon(object):

    def __init__(self, dist, module):
        self.dist = dist
        self.__name__ = dist.project_name
        self.__parent__ = module


class Config(object):

    def __init__(self, actions):
        self.registry = config.registry
        self.actions = actions
        self.storage = config.registry.storage


class AddonsView(view.View):
    view.pview(
        context = AddonsModule,
        template = view.template('ptah.addon:templates/addons.pt'))

    def update(self):
        data = []

        for dist in ADDONS.values():
            data.append(dist)

        self.addons = data

        if 'form.button.install' in self.request.POST:
            for name in self.request.POST.getall('addon'):
                for dist in self.addons:
                    if dist.project_name == name:
                        # activate egg
                        dist.activate()
                        pkg_resources.working_set.add(dist)

                        # load actions
                        actions = directives.scan(name, set())
                        cfg = Config(actions)

                        # pre install step
                        distmap = pkg_resources.get_entry_map(dist, 'ptah')

                        if 'pre_install' in distmap:
                            distmap['pre_install'].load()(cfg)

                        for action in actions:
                            cfg.action = action
                            action(cfg)

                        config.registry.storage['actions'].extend(actions)

                        if 'post_install' in distmap:
                            distmap['post_install'].load()()


class AddonView(view.View):
    view.pview(
        context = Addon,
        template = view.template('ptah.addon:templates/package.pt'))

    def update(self):
        actions = directives.scan(self.context.dist.project_name, set())

        info = {}
        for action in actions:
            d = action.discriminator[0]
            d_data = info.setdefault(d, {})
            mod_data = d_data.setdefault(action.info.module.__name__, [])
            mod_data.append(action)

        self.data = info

        self.ndata = ndata = {}
        for tp, d in info.items():
            actions = []
            for k, ac in d.items():
                actions.extend(ac)

            ndata[tp] = actions

        itypes = []
        intros = config.registry.storage[INTROSPECT_ID]
        for key, cls in intros.items():
            if key in self.data:
                itypes.append((cls.title, cls(self.request)))

        itypes.sort()
        self.itypes = [it for _t, it in itypes]
