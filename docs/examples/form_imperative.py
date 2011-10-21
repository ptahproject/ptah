""" This is an example of useing form (imperative style). """
import ptah
from pprint import pprint
from paste.httpserver import serve
from pyramid.httpexceptions import HTTPFound
from ptah import view, form, cms


@view.pview('test-form.html', context=cms.Content)
def form_view(context, request):

    myform = form.Form(context, request)

    # define fields for form
    myform.fields = form.Fieldset(

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

    # form actions
    def cancelAction(form):
        raise HTTPFound(location='.')

    def updateAction(form):
        data, errors = form.extract()

        if errors:
            form.message(errors, 'form-error')
            return

        pprint(data)

        form.context.title = data['title']
        form.context.description = data['description']
        form.message('Content has been updated.', 'info')
        raise HTTPFound(location='.')

    myform.buttons.add_action('Update', action=updateAction)
    myform.buttons.add_action('Cancel', action=cancelAction)

    # form default values
    myform.content = {'title': context.title,
                      'description': context.description}

    # prepare form
    myform.update()

    # render form
    res = myform.render()

    # optional, render form in layout
    layout = view.LayoutRenderer('')
    return layout(context, request, res)


if __name__ == '__main__':
    """ ...

    """
    app = ptah.make_wsgi_app({'settings':r'./ptah.ini'})
    serve(app, host='0.0.0.0')
