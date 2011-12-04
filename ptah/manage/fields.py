""" ptah.form fields """
from ptah import view, config, manage
from ptah.form.field import FIELD_ID, PREVIEW_ID


@manage.module('fields')
class FieldsModule(manage.PtahModule):
    __doc__ = ('A preview and listing of all form fields in the '
      'application. This is useful to see what fields are available. '
      'You may also interact with the field to see how it works in '
      'display mode.')

    title = 'Field types'


class FieldsView(view.View):
    view.pview(
        context = FieldsModule,
        template = view.template('ptah.manage:templates/fields.pt'))

    def update(self):
        data = []

        fields = config.get_cfg_storage(FIELD_ID)
        previews = config.get_cfg_storage(PREVIEW_ID)

        for name, cls in fields.items():
            data.append({'name': name,
                         'doc': cls.__doc__,
                         'preview': previews.get(cls)})

        self.fields = sorted(data, key = lambda item: item['name'])
