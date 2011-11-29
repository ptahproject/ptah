""" settings module """
from ptah import view, manage
from ptah.config.settings import get_settings_ob


class SettingsModule(manage.PtahModule):
    __doc__ = 'The current settings which include defaults not used by .ini'

    title = 'Settings'
    manage.module('settings')


class SettingsView(view.View):
    view.pview(
        context = SettingsModule,
        template = view.template('ptah.manage:templates/settings.pt'))

    __doc__ = "Settings module page."
    __intr_path__ = '/ptah-manage/settings/index.html'

    def update(self):
        groups = get_settings_ob().items()

        data = []
        for name, group in sorted(groups):
            title = group.title or name
            description = group.description

            schema = []
            for node in group.schema:
                value = node.serialize(group[node.name])

                schema.append(
                    ({'name': '%s.%s'%(name, node.name),
                      'value': '%s: %s'%(node.typ.__class__.__name__, value),
                      'title': node.title,
                      'description': node.description,
                      'default': node.default}))

            data.append(
                ({'title': title,
                  'description': description,
                  'schema': schema}))

        return {'data': data}
