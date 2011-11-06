================
Ptah Walkthrough
================

You should have virtualenv with ptah installed.  Let's create an add-on::

  ~/venv/src$ ../bin/paster create -t ptah101 mypkg
  ~/venv/src$ cd mypkg
  ~/venv/src/mypkg$ ../../bin/python setup.py develop

Now lets start the system.  The --reload will start file watcher in paster
and will restart the process anytime a .py file is changed.

  ~/venv/src/$ ../bin/paster serve pkg/mypkg --reload

Let's goto http://localhost:6543/

  * What you are seeing is a Pyramid ApplicationFactory registered for /
  
  * This ApplicationFactory creates an instance of ptah.cms.ApplicationRoot 
    which can be found at mkpkg/app.py

  * You can have multiple ApplicationFactorys in a single Pyramid process.

  * Ptah ApplicationRoot's are a persistent container in the database.

Let's login and goto Ptah Manage, http://localhost:6543/ptah-manage/ to see
the ApplicationRoot.  I said the ApplicationRoot (AppRoot) is a persistent
container.  So let's goto SQLAlchemy are take a look in the database.

Click SQLAlchemy -> click ptah_cms_nodes -> see rows in the table.  Some
things to note:

  - The ApplicationRoot type value is 'ptah+app:mkpkg-app' and it has a uri
    and if you scroll over you will see JSON in the roles column.  That 
    describes which Principal (aka User) has that role.

  - You can click Edit and modify any of those values.  Obviously you can
    easily break the entire application by careless edits.

  - All tables inherient from the ptah_cms_nodes table.  For every data/content
    record in the entire Ptah system will have a entry in the ptah_cms_nodes.

There should be a record in ptah_cms_nodes with a uri starting with `cms+page`.
Let's go check out that record in ptah_cmsapp_nodes.  Go back to the SQLAlchemy
module which lists all of the models/tables in the application.  Click on
`ptah_cmsapp_pages` and you will see the Page records.  Click Edit.  Useful
notes:

  - A Field, see ptah.form.fields, can be registered against as a default
    against as SQLAlchemy column type.  Or you can pass in a particular 
    field_type in your model to specify what Field you want to use for that 
    Model's field.
  
  - In this case ptah_cmsapp_page.text has been registered with the 
    field_type: tinymce.  The relevant code from ptah.cmsapp.content.page::
      
      class Page(cms.Content):

        __tablename__ = 'ptah_cmsapp_pages'

        __type__ = cms.Type(
            'page',
            title = 'Page',
            description = 'A page in the site.',
            permission = AddPage,
            name_suffix = '.html',
            )

        text = sqla.Column(sqla.Unicode,
                           info = {'field_type': 'tinymce'})
                           
  - Lastly you will notice in the Page model that it inherients from cms.Content
    which means this model has all of the attributes of the base Content class.
    You can find those attributes in ptah_cms_content; which is where all 
    content-oriented (as opposed to data-oriented) records live.  Before you
    leave the ptah_cmsapp_pages screen note the ID field value.
  
To round this all off we can go look at the content-oriented table, 
`ptah_cms_content`.  Go back to the SQLAlchemy module where all of the models
are registered and click `ptah_cms_content` to list all records for that
model.  Look for the record whose ID matches the page record you just looked
at in ptah_cmsapp_pages table.  This is data from the same record.  That
is right, the Page content model exists in ptah_cms_nodes, ptah_cms_content,
and ptah_cmsapp_pages.  It's essentially inheritance which is a familiar
concept for object oriented programmers.  Looking at ptah_cms_content you
can note:

  - path is an attribute which looks kinda strange.  This path attribute
    represents the ApplicationRoot and the relative path where the content
    exists in the heriarchy.  While it looks ugly (due to the ApplicationRoot
    URI in the path) its necessary for efficient and flexible lookup usage
    Ptah and you will be doing in the future.
  
  - Let's click EDIT on one of the ptah_cms_content records.  You will 
    notice that field-type have been assigned to the cms.Content class.  
    If you click on Created or Modified you will notice it uses JQuery date
    widget.
  
NOTE: Someone who has used frameworks will have asked themselves, "Well,
if those field-type's are defined on Content for those widget, how can
I override them w/o forking or touching the internal code? "  The answer 
is Yes you can override them because the internal implementation uses 
a FieldFactory.  But this is a advanced concept and we defer for now.

Form Fields
-----------

Remember some of those fields we saw when editing the SQLAlchemy models?
Well the `Form fields` module is a list of all available Field's registered
in the system.  By the time you read this, I hope, there will be dozens of
add-on Fields available to download and use.  Fields can be reused between 
Ptah installations.  While you dont need to make resuable software upfront;
if you do - you can share/reuse it.

  - If you scroll all the way down you will see the tinymce Field that
    we saw in the ptah_cmsapp_pages Edit screen.
  
  - There is an API that Field developer use to register a preview of their
    widget.  Use this so that a preview is available for your widget.  You
    can see default widget previews in `path/manage/fieldpreviews.py`

  - Do not expect to interact with a Field preview; its a READONLY preview.







