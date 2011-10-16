""" memphis.form fields """
from memphis import view, form, config
from memphis.form.field import FIELD_ID, PREVIEW_ID

import ptah


class FieldsModule(ptah.PtahModule):
    __doc__ = 'Memphis form fields.'

    title = 'Form fields'
    ptah.manageModule('fields')


class FieldsView(view.View):
    view.pyramidview(
        context = FieldsModule,
        template = view.template('ptah_modules:templates/fields.pt'))

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
