""" settings module """
import ptah
from ptah import config, view


class SettingsModule(ptah.PtahModule):
    """ Memphis settings management module. """

    title = 'Settings'
    ptah.manageModule('settings')


class SettingsView(view.View):
    view.pview(
        context = SettingsModule,
        template = view.template('ptah.manage:templates/settings.pt'))

    __doc__ = "Settings module page."
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
