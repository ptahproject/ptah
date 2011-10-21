Example of Content Model
------------------------

Create a file called link.py inside of your scaffolding.  You can copy
and paste this code into the file called link.py; restart paster and
click Add Content or look at SQLAlchemy in Ptah Manage.

A simple model::

    import sqlalchemy as sqla
    from pyramid.httpexceptions import HTTPFound

    from ptah import view, form, cms
    from ptah import checkPermission
    
    class Link(cms.Content):
        __tablename__ = 'ptah_cms_link'
        __type__ = cms.Type('link', permission=cms.AddContent)
        href = sqla.Column(sqla.Unicode)

    @view.pview(context=Link, permission=cms.View, layout='page')
    def link_view(context, request):
        """ This is a default view for a Link model.
            If user has permission to edit Link a form will be displayed.
            If user do not have ability to edit Link; they will be redirected.
        """
        can_edit = checkPermission(cms.ModifyContent, context)

        if can_edit:
            vform = form.DisplayForm(context, request)
            vform.fields = Link.__type__.fieldset
            vform.content = {
                'title': context.title,
                'description': context.description,
                'href': context.href}
            vform.update()

            # Uncomment below if you do not want the layout wrapper
            #return vform.render()

            layout = view.query_layout(request, context)
            return layout(vform.render())

        raise HTTPFound(location=context.href)

Why Subclass from Content?
~~~~~~~~~~~~~~~~~~~~~~~~~~

The Ptah Content model is quite high level and provides a lot of functionality.
By inherienting from :py:class:ptah.cms.content.Content you get the 
following:

  - Automatically get polymorphism with ptah_cms_node table.
  
  - You do not need to specify a "uri resolver"
  
  - You will get fieldset representation (schema-ish) from model
  
  - You get security at the model level
  
  - Your model can participate in REST api without any work
  
  - Your model will have events thrown upon creation/delete/update
  
  - Automatically generated Add/Edit forms
  
  - Models will be available in Application content heirarchy


Why Not Subclass from Content?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you do not want to subclass from ptah.cms.content.Content there are two
other options.  The first is you do not have to partcipate in SQLAlchemy at
all.  You can use Ptah as a library and instrument the API yourself.  

The other option is your model can subclass :py:class:ptah.cms.node.Node 
