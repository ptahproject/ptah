""" default content forms """
import re
import colander
from memphis import view, form
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPFound

import ptah_cms
from ptah_cms.interfaces import IContent
from ptah_cms.permissions import ModifyContent


class AddForm(form.Form):

    tinfo = None
    container = None

    name_suffix = ''
    name_fields = form.Fields(ptah_cms.ContentNameSchema)

    @reify
    def fields(self):
        return form.Fields(self.tinfo.schema)

    @reify
    def label(self):
        return 'Add %s'%self.tinfo.title

    @reify
    def description(self):
        return self.tinfo.description

    def chooseName(self, content, **kw):
        name = kw.get('title', u'')
        
        name = re.sub(
            r'-{2,}', '-',
            re.sub('^\w-|-\w-|-\w$', '-',
                   re.sub(r'\W', '-', name.strip()))).strip('-').lower()

        n = '%s%s'%(name, self.name_suffix)
        i = 1
        while n in self.container:
            i += 1
            n = u'%s-%s%s'%(name, i, suffix)

        return n.replace('/', '-').lstrip('+@')

    def update(self):
        self.container = self.context
        self.name_suffix = getattr(self.tinfo, 'name_suffix', '')

        self.tinfo.checkContext(self.context)
        super(AddForm, self).update()

    def updateWidgets(self):
        super(AddForm, self).updateWidgets()

        self.name_widgets = \
            form.FieldWidgets(self.name_fields, self, self.request)
        self.name_widgets.mode = self.mode
        self.name_widgets.update()

    def validate(self, data, errors):
        super(AddForm, self).validate(data, errors)

        if '__name__' in data:
            widget = self.name_widgets['__name__']

            name = data['__name__']
            if name in self.container.keys():
                error = colander.Invalid(
                    self.name_fields['__name__'].node, 'Name already in use')
                errors.append(error)

    def extractData(self, setErrors=True):
        data, errors = self.widgets.extract(setErrors)

        name_data, name_errors = self.name_widgets.extract(setErrors)
        if name_errors:
            errors.extend(name_errors)

        data.update(name_data)
        return data, errors

    def create(self, **data):
        content = self.tinfo.create(**data)
        ptah_cms.Session.add(content)
        return content

    def createAndAdd(self, **data):
        content = self.create(**data)
        
        self.request.registry.notify(
            ptah_cms.events.ContentCreatedEvent(content))

        name = data['__name__']
        if not name:
            name = self.chooseName(content, **data)

        self.container[name] = content
        return content

    @form.button('Add', actype=form.AC_PRIMARY)
    def saveHandler(self):
        data, errors = self.extractData()

        if errors:
            self.message(errors, 'form-error')
            return

        content = self.createAndAdd(**data)

        self.message('New content has been created.')
        raise HTTPFound(location=content.__name__)

    @form.button('Cancel')
    def cancelHandler(self):
        raise HTTPFound(location='.')


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
        return form.Fields(self.tinfo.schema)

    def getContent(self):
        return self.context

    def update(self):
        self.tinfo = self.context.__type__

        super(EditForm, self).update()

    @form.button('Save', actype=form.AC_PRIMARY)
    def saveHandler(self):
        data, errors = self.extractData()

        if errors:
            self.message(errors, 'form-error')
            return

        for attr, value in data.items():
            setattr(self.context, attr, value)

        self.request.registry.notify(
            ptah_cms.events.ContentModifiedEvent(self.context))

        self.message("Changes have been saved.")
        raise HTTPFound(location='.')

    @form.button('Cancel')
    def cancelHandler(self):
        raise HTTPFound(location='.')
