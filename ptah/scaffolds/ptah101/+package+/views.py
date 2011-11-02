from pyramid.httpexceptions import HTTPFound
from ptah import view, form, cms

from intro.root import ApplicationRoot
from intro.models import Link

# register static asset directory
# logo can be found at /static/intro/logo.png
view.static('intro', 'intro:static')

class HomepageView(view.View):
    """ Homepage view """
    view.pview(context=ApplicationRoot,
               template=view.template('templates/homepage.pt'))

    def get_links(self):
        return cms.Session.query(Link).all()

class LinkListingView(view.View):
    """ Show a listing of Link models """
    pass


@view.pview('contact-us.html', context=ApplicationRoot)
def contact_us(context, request):

    contactform = form.Form(context, request)
 
    contactform.fields = form.Fieldset(

        form.TextField(
            'fullname',
            title = u'First & Last Name'),  

        form.TextField(
            'phone',
            title = u'Telephone number'),

        form.TextField(
            'email',
            title = u'Your email',
            description = u'Please provide email address.',
            validator = form.Email()),

        form.TextAreaField(
            'subject',
            title = u'How can we help?',
            missing = u''), # field use this value is request doesnt contain
                            # field value, effectively field is required
                            # if `missing` is not specified
        )

    # form actions
    def cancelAction(form):
        raise HTTPFound(location='.')

    def updateAction(form):
        data, errors = form.extract()

        if errors:
            form.message(errors, 'form-error')
            return

        # form.context is ...
        form.context.fullname = data['fullname']
        form.context.phone = data['phone']
        form.context.email = data['email']
        form.context.subject = data['subject']

        # form succeeded; want to send email?  put data in database?
        # you would add that logic here.

        form.message('Content has been updated.', 'info')
        raise HTTPFound(location='.')

    contactform.buttons.add_action('Update', action=updateAction)
    contactform.buttons.add_action('Cancel', action=cancelAction)

    # form default values
    contactform.content = {'title': context.title,
                           'description': context.description}

    # prepare form
    contactform.update()

    # render form into HTML
    res = contactform.render()

    # optional, render form in layout
    layout = view.LayoutRenderer('')
    return layout(context, request, res)

