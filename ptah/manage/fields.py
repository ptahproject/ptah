""" ptah.form fields """
from ptah import view, config, manage
from ptah.form.field import FIELD_ID, PREVIEW_ID


class FieldsModule(manage.PtahModule):
    __doc__ = u'A listing of all registered fields.'
    
    title = 'Form fields'
    manage.module('fields')


class FieldsView(view.View):
    view.pview(
        context = FieldsModule,
        template = view.template('ptah.manage:templates/fields.pt'))

    def update(self):
        data = []

        fields = config.registry.storage[FIELD_ID]
        previews = config.registry.storage[PREVIEW_ID]

        for name, cls in fields.items():
            data.append({'name': name,
                         'doc': cls.__doc__,
                         'preview': previews.get(cls)})

        data.sort()
        self.fields = data
