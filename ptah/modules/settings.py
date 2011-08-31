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


class MainView(view.View):
    view.pyramidView(
        'index.html', ISettingsModule, 'ptah-manage', default=True, layout='',
        template = view.template(
            'ptah.modules:templates/settings.pt', nolayer=True))

    __doc__ = "Settings page."
    __intr_path__ = '/ptah-manage/settings/index.html'

    def update(self):
        groups = config.Settings.items()
        groups.sort()

        data = []
        for name, group in groups:
            title = group.title or name
            description = group.description

            schema = []
            for node in group.schema:
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
