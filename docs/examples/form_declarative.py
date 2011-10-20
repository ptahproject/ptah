""" This is an example of useing form (imperative style). """
import ptah
from pprint import pprint
from paste.httpserver import serve
from pyramid.httpexceptions import HTTPFound
from ptah import cms, view, form


class MyForm(form.Form):
    view.pview('test-form.html', context=cms.Content)

    # define fields for form
    fields = form.Fieldset(

        form.TextField(
            'title',
            title = u'Title'),  # field title

        form.TextAreaField(
            'description',
            title = u'Description',
            missing = u''), # field use this value is request doesnt contain
                            # field value, effectively field is required
                            # if `missing` is not specified
        form.TextField(
            'email',
            title = u'E-Mail',
            description = u'Please provide email address.',
            validator = form.Email(), # email validator
            ),
        )

    # form default values
    def form_content(self):
        return {'title': self.context.title,
                'description': self.context.description}

    @form.button('Update')
    def update_handler(self):
        data, errors = self.extract()

        if errors:
            self.message(errors, 'form-error')
            return

        pprint(data)

        self.context.title = data['title']
        self.context.description = data['description']
        self.message('Content has been updated.', 'info')
        raise HTTPFound(location='.')

    @form.button('Cancel')
    def cancel_handler(self):
        raise HTTPFound(location='.')


if __name__ == '__main__':
    """ ...

    """
    app = ptah.make_wsgi_app({'settings':r'./ptah.ini'})
    serve(app, host='0.0.0.0')
