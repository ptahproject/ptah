""" ptah.form fields """
from ptah import view, config, manage
from ptah.form.field import FIELD_ID, PREVIEW_ID


class FieldsModule(manage.PtahModule):
    """A preview and listing of all form fields in the application.
       This is useful to see what fields are available.  You may also
       interact with the field to see how it works in display mode.
    """
    title = 'Field types'
    manage.module('fields')


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

        data.sort()
        self.fields = data
