""" ptah.form fields """
import ptah
from ptah.form.field import FIELD_ID, PREVIEW_ID
from pyramid.view import view_config


@ptah.manage.module('fields')
class FieldsModule(ptah.manage.PtahModule):
    __doc__ = ('A preview and listing of all form fields in the '
      'application. This is useful to see what fields are available. '
      'You may also interact with the field to see how it works in '
      'display mode.')

    title = 'Field types'


@view_config(
    context=FieldsModule, wrapper=ptah.wrap_layout(),
    renderer='ptah.manage:templates/fields.pt')

class FieldsView(ptah.View):
    """ Fields manage module view """

    def update(self):
        data = []

        fields = ptah.get_cfg_storage(FIELD_ID)
        previews = ptah.get_cfg_storage(PREVIEW_ID)

        for name, cls in fields.items():
            data.append({'name': name,
                         'doc': cls.__doc__,
                         'preview': previews.get(cls)})

        self.fields = sorted(data, key = lambda item: item['name'])
