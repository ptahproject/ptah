""" settings module """
import ptah
from ptah import view, manage, config
from ptah.settings import SETTINGS_GROUP_ID
from pyramid.httpexceptions import HTTPFound


@manage.module('settings')
class SettingsModule(manage.PtahModule):
    __doc__ = 'The current settings which include defaults not used by .ini'

    title = 'Settings'

    def __getitem__(self, key):
        grp = ptah.get_settings(key, self.request.registry)
        if grp is not None and grp.__ttw__:
            return SettingsWrapper(grp, self)
        raise KeyError(key)


class SettingsWrapper(object):

    def __init__(self, grp, mod):
        self.__name__ = grp.__name__
        self.__parent__ = mod
        self.group = grp


class SettingsView(view.View):
    view.pview(
        context = SettingsModule,
        template = view.template('ptah.manage:templates/settings.pt'))

    __doc__ = "Settings module page."
    __intr_path__ = '/ptah-manage/settings/index.html'

    def update(self):
        groups = config.get_cfg_storage(SETTINGS_GROUP_ID).items()

        data = []
        for name, group in sorted(groups):
            title = group.__title__ or name
            description = group.__description__

            schema = []
            for field in group.__fields__.values():
                schema.append(
                    ({'name': '{0}.{1}'.format(name, field.name),
                      'type': field.__class__.__name__,
                      'value': field.dumps(group[field.name]),
                      'title': field.title,
                      'description': field.description,
                      'default': field.dumps(field.default)}))

            data.append(
                ({'title': title,
                  'description': description,
                  'schema': schema,
                  'name': group.__name__,
                  'ttw': group.__ttw__}))

        return {'data': sorted(data, key=lambda item: item['title'])}


class EditForm(ptah.form.Form):
    view.pview(context = SettingsWrapper)

    @property
    def fields(self):
        return self.context.group.__fields__

    def form_content(self):
        return self.context.group

    @ptah.form.button('Modify', actype=ptah.form.AC_PRIMARY)
    def modify_handler(self):
        data, errors = self.extract()
        if errors:
            self.message(errors, 'form-error')
            return

        self.message("Settings have been modified.")
        self.context.group.updatedb(**data)
        raise HTTPFound('../#{0}'.format(self.context.group.__name__))

    @ptah.form.button('Reset defaults', actype=ptah.form.AC_INFO)
    def reset_handler(self):
        pass

    @ptah.form.button('Back')
    def back_handler(self):
        raise HTTPFound('..')
