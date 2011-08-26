""" settings module """
import ptah
from zope import interface
from memphis import config, view

from zope import interface


class ISettingsModule(ptah.IPtahModule):
    """ Settings module """


class SettingsModule(ptah.PtahModule):
    """ Memphis settings management module. """

    config.utility(name='settings')
    interface.implementsOnly(ISettingsModule)

    name = 'settings'
    title = 'Settings'

    def __getitem__(self, key):
        #return Package(self.packagesDict[key], self, self.request)
        raise KeyError(key)


class MainView(view.View):
    view.pyramidView(
        'index.html', ISettingsModule, route='ptah-manage', default = True,
        template = view.template(
            'ptah.modules:templates/settings.pt', nolayer=True))

    def update(self):
        groups = config.Settings.items()
        groups.sort()

        data = []
        for name, group in groups:
            title = group.title or name
            description = group.description

            schema = []
            for node in group.schema:
                #default = '<required>' if node.required else node.default
                value = node.serialize(group[node.name])

                schema.append(
                    ({'name': '%s.%s'%(name, node.name), 
                      'value': '%s: %s'%(node.typ.__class__.__name__, value),
                      'title': node.title, 
                      'description': node.description}))

            data.append(
                ({'title': title,
                  'description': description,
                  'schema': schema}))

        return {'data': data}
