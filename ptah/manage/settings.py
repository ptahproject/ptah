""" settings module """
from ptah import view, manage
from ptah.settings import get_settings_groups


@manage.module('settings')
class SettingsModule(manage.PtahModule):
    __doc__ = 'The current settings which include defaults not used by .ini'

    title = 'Settings'


class SettingsView(view.View):
    view.pview(
        context = SettingsModule,
        template = view.template('ptah.manage:templates/settings.pt'))

    __doc__ = "Settings module page."
    __intr_path__ = '/ptah-manage/settings/index.html'

    def update(self):
        groups = get_settings_groups().items()

        data = []
        for name, group in sorted(groups):
            title = group.__title__ or name
            description = group.__description__

            schema = []
            for field in group.__fields__.values():
                value = field.dumps(group[field.name])

                schema.append(
                    ({'name': '%s.%s'%(name, field.name),
                      'value': '%s: %s'%(field.__class__.__name__, value),
                      'title': field.title,
                      'description': field.description,
                      'default': field.dumps(field.default)}))

            data.append(
                ({'title': title,
                  'description': description,
                  'schema': schema}))

        return {'data': data}
