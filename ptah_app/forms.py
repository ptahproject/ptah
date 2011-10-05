""" default content forms """
import re
from memphis import config, view, form
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPFound

import ptah_cms
from ptah_cms.interfaces import IContent
from ptah_cms.permissions import ModifyContent


class AddForm(form.Form):

    tinfo = None
    container = None

    name_show = True
    name_suffix = ''
    name_widgets = None
    name_fields = ptah_cms.ContentNameSchema

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
        name = kw.get('title', u'')

        name = re.sub(
            r'-{2,}', '-',
            re.sub('^\w-|-\w-|-\w$', '-',
                   re.sub(r'\W', '-', name.strip()))).strip('-').lower()

        suffix = self.name_suffix
        n = '%s%s'%(name, suffix)
        i = 1
        while n in self.container:
            i += 1
            n = u'%s-%s%s'%(name, i, suffix)

        return n.replace('/', '-').lstrip('+@')

    def update(self):
        self.name_suffix = getattr(self.tinfo, 'name_suffix', '')

        self.tinfo.checkContext(self.container)
        super(AddForm, self).update()

    def updateWidgets(self):
        super(AddForm, self).updateWidgets()

        if self.name_show:
            self.name_widgets = \
                   form.FormWidgets(self.name_fields, self, self.request)
            self.name_widgets.mode = self.mode
            self.name_widgets.update()

    def validate(self, data, errors):
        super(AddForm, self).validate(data, errors)

        if '__name__' in data and data['__name__']:
            widget = self.name_widgets['__name__']

            name = data['__name__']
            if name in self.container.keys():
                error = form.Invalid(
                    self.name_fields['__name__'].node, 'Name already in use')
                errors.append(error)

    def extract(self, setErrors=True):
        data, errors = self.widgets.extract(setErrors)

        if self.name_show:
            name_data, name_errors = self.name_widgets.extract(setErrors)
            if name_errors:
                errors.extend(name_errors)

            data.update(name_data)

        return data, errors

    def create(self, **data):
        name = data.get('__name__')
        if not name:
            name = self.chooseName(**data)

        content = ptah_cms.cms(self.container).create(
            self.tinfo.__uri__, name, **data)

        return content

    @form.button('Add', actype=form.AC_PRIMARY)
    def saveHandler(self):
        data, errors = self.extract()

        if errors:
            self.message(errors, 'form-error')
            return

        content = self.create(**data)

        self.message('New content has been created.')
        raise HTTPFound(location=self.nextUrl(content))

    @form.button('Cancel')
    def cancelHandler(self):
        raise HTTPFound(location='.')

    def nextUrl(self, content):
        return self.request.resource_url(content)


view.registerPagelet(
    'form-actions', AddForm,
    template = view.template('ptah_app:templates/form-actions.pt'))


class EditForm(form.Form):
    view.pyramidView('edit.html', IContent, permission=ModifyContent)

    @reify
    def label(self):
        return 'Modify content: %s'%self.tinfo.title

    @reify
    def fields(self):
        return self.tinfo.fieldset

    def getContent(self):
        data = {}
        for name, field in self.tinfo.fieldset.items():
            data[name] = getattr(self.context, name, field.default)

        return data

    def update(self):
        self.tinfo = self.context.__type__

        super(EditForm, self).update()

    def applyChanges(self, **data):
        ptah_cms.cms(self.context).update(**data)

    @form.button('Save', actype=form.AC_PRIMARY)
    def saveHandler(self):
        data, errors = self.extract()

        if errors:
            self.message(errors, 'form-error')
            return

        self.applyChanges(**data)
        #config.notify(ptah_cms.events.ContentModifiedEvent(self.context))

        self.message("Changes have been saved.")
        raise HTTPFound(location=self.nextUrl())

    @form.button('Cancel')
    def cancelHandler(self):
        raise HTTPFound(location=self.nextUrl())

    def nextUrl(self):
        return '.'
