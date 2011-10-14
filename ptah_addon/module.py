""" addon system """
import ptah
import pkg_resources
from memphis import config, view, form
from memphis.config import directives

from core import ADDONS


class AddonModule(ptah.PtahModule):
    """Add-ons management"""

    title = 'Add-ons'
    ptah.manageModule('addons')


class AddonView(view.View):
    view.pyramidview(
        context = AddonModule,
        template = view.template('ptah_addon:templates/addon.pt'))

    def update(self):
        data = []

        for dist in ADDONS:
            data.append(dist)

        self.addons = data

        if 'form.button.install' in self.request.POST:
            for name in self.request.POST.getall('addon'):
                for dist in self.addons:
                    if dist.project_name == name:
                        dist.activate()
                        actions = directives.scan(name, set())
                        pkg_resources.working_set.add(dist)
                        for action in actions:
                            action()
