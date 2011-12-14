""" content helper forms """
import re
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPFound

import ptah
from ptah import form
from ptah.cms.security import wrap
from ptah.cms.interfaces import ContentNameSchema


class AddForm(form.Form):

    tinfo = None
    container = None

    name_show = True
    name_suffix = ''
    name_widgets = None
    name_fields = ContentNameSchema

    def __init__(self, context, request):
        self.container = context
        super(AddForm, self).__init__(context, request)

    @reify
    def fields(self):
        return self.tinfo.fieldset

    @reify
    def label(self):
        return 'Add %s'%self.tinfo.title

    @reify
    def description(self):
        return self.tinfo.description

    def chooseName(self, **kw):
        name = kw.get('title', '')

        name = re.sub(
            '-{2,}', '-',
            re.sub('^\w-|-\w-|-\w$', '-',
                   re.sub(r'\W', '-', name.strip()))).strip('-').lower()

        suffix = self.name_suffix
        n = '%s%s'%(name, suffix)
        i = 0
        while n in self.container:
            i += 1
            n = '%s-%s%s'%(name, i, suffix)

        return n.replace('/', '-').lstrip('+@')

    def update(self):
        self.name_suffix = getattr(self.tinfo, 'name_suffix', '')

        self.tinfo.check_context(self.container)
        return super(AddForm, self).update()

    def update_widgets(self):
        super(AddForm, self).update_widgets()

        if self.name_show:
            self.name_widgets = \
                   form.FormWidgets(self.name_fields, self, self.request)
            self.name_widgets.mode = self.mode
            self.name_widgets.update()

    def validate(self, data, errors):
        super(AddForm, self).validate(data, errors)

        if self.name_widgets and '__name__' in data and data['__name__']:
            name = data['__name__']
            if name in self.container.keys():
                error = form.Invalid(
                    self.name_widgets['__name__'], 'Name already in use')
                error.field = self.name_widgets['__name__']
                errors.append(error)

    def extract(self):
        data, errors = self.widgets.extract()

        if self.name_show:
            name_data, name_errors = self.name_widgets.extract()
            if name_errors:
                errors.extend(name_errors)

            data.update(name_data)

        return data, errors

    def create(self, **data):
        name = data.get('__name__')
        if not name:
            name = self.chooseName(**data)

        return wrap(self.container).create(
            self.tinfo.__uri__, name, **data)

    @form.button('Add', actype=form.AC_PRIMARY)
    def add_handler(self):
        data, errors = self.extract()

        if errors:
            self.message(errors, 'form-error')
            return

        content = self.create(**data)

        self.message('New content has been created.')
        return HTTPFound(location=self.get_next_url(content))

    @form.button('Cancel')
    def cancel_handler(self):
        return HTTPFound(location='.')

    def get_next_url(self, content):
        return self.request.resource_url(content)


ptah.snippet.register(
    'form-actions', AddForm, renderer='ptah.cms:form-actions.pt')


class EditForm(form.Form):

    @reify
    def label(self):
        return 'Modify content: %s'%self.tinfo.title

    @reify
    def fields(self):
        return self.tinfo.fieldset

    def form_content(self):
        data = {}
        for name, field in self.tinfo.fieldset.items():
            data[name] = getattr(self.context, name, field.default)

        return data

    def update(self):
        self.tinfo = self.context.__type__

        return super(EditForm, self).update()

    def apply_changes(self, **data):
        wrap(self.context).update(**data)

    @form.button('Save', actype=form.AC_PRIMARY)
    def save_handler(self):
        data, errors = self.extract()

        if errors:
            self.message(errors, 'form-error')
            return

        self.apply_changes(**data)

        self.message("Changes have been saved.")
        return HTTPFound(location=self.get_next_url())

    @form.button('Cancel')
    def cancel_handler(self):
        return HTTPFound(location=self.get_next_url())

    def get_next_url(self):
        return '.'
