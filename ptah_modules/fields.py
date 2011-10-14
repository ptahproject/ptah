""" memphis.form fields """
from memphis import view, form
from memphis.form.field import fields, previews

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

        for name, cls in fields.items():
            data.append({'name': name,
                         'doc': cls.__doc__,
                         'preview': previews.get(cls)})

        data.sort()
        self.fields = data
