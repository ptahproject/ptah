Interactive Prompt with Ptah
============================

[XXX] Show how to create a pyramid request

You can use any Python interpreter to import and start Ptah easily. Starting up and getting familiar.  In less than 10 seconds::

  $ python

  >>> from mephis import config
  >>> config.initialize() # scans for all packages in sys.path
  >>> config.initialize_settings( {'settings':'/path/to/ptah_settings.ini'} )

Voila your interpreter is fully initialized.  We do not have any convienance
functionality at this time.  The public API will be enough.

Let us query all content in the system.

  >>> from ptah.cms import Session, Content
  >>> Session.query(Content).all()

  [<ptah.cms.root.ApplicationRoot at 0x3df04b0>,
   <ptah.cmsapp.content.page.Page at 0x3df1330>,
   <ptah.cmsapp.content.folder.Folder at 0x3df1810>]

Creating content is straight forward.  If you manipulate SQL directly you will not participate in the event subsystem of Ptah.  So lets create a piece of content with and without events.

  >>> from ptah.cmsapp.content.page import Page
  >>> page = Page(title='Manually created')
  >>> Session.add(page)
  >>> import transaction; transaction.commit()

If you goto the Ptah App interface, http://localhost:8080/ you will not see your page.  But if you goto Ptah Manage interface, http://localhost:8080/ptah-manage/ then goto SQLAlchemy and goto the ptah_cms_pages table you *will* see your content.  Lets continue using the low-level API (SQL).  First let's see the new page via SQL::

  >>> Session.query(Content).all()
  [<ptah.cms.root.ApplicationRoot at 0x3df04b0>,
   <ptah.cmsapp.content.page.Page at 0x3df1330>,
   <ptah.cmsapp.content.folder.Folder at 0x3df1810>,
   <ptah.cmsapp.content.page.Page at 0x3df16b2>]

Let's add the relationship between Page and its container (ApplicationRoot) so we can see our new page inside the Ptah App interface.

  >>> import ptah.cms import ApplicationRoot
  >>> root=Session.query(ApplicationRoot).filter_by(
  ...     __name__='root').first()
  >>> root['manually-created']=page
  >>> import transaction; transaction.commit()

sql way

  >>> page.description = 'description'
  >>> transaction.commit()

cms way, `update` method examines type info schema and sets attributes
that awailable in schema.  this will also notify the framework with appropriate ptah.cms.events.

  >>> page.update(description='description')

show schema

  >>> for field in Page.__type__.fieldset:
  ...    print getattr(page, field.name, None)

show fields of schema (html)

  >>> from ptah import form
  >>> request=request (description='We are not sending title',
          text='<p>This is some body text for WYSIWYG field</p>')
  >>> eform = form.Form(page,  )
  >>> eform.fields = page.__type__.fieldset
  >>> eform.update() # initialized the fieldset to accept request
  >>> data, errors = eform.extract()

  >>> print errors
  [Invalid<TextField "title": "Required">]

  >>> print errors[0].field
  <TextField 'title'>

  >>> print errors[0].msg
  "Required"

If we add `title` to request, lets see if the errors go away.
  >>> request=request(title='a title',
          description='brief description',
          text='<p>some html</p>')
  >>> eform.request = request
  >>> eform.update()
  >>> data, errors = eform.extract()
  >>> print errors
  []

We no longer have errors.

[XXX] use datetime in request since its more interesting since it will deserialize into a datetime object.

data is a dictionary which contains python builtins since the Form machinery has converted strings (HTTP Request) to python structures.  errors is a list of
  >>> print eform.render()

Now lets use the form system to set attributes on the page.
  >>> TODO

load and load_parents

These two functions can be found in ptah.cms.node.load and ptah.cms.node.load_parents.  This API is useful when you want to work with hierarchies or security.

First lets show non-initialized node
  >>> p=Session.query(Content).filter_by(title='Manually created').first()
  >>> p.__parent__
  >>>

This is because there is no parent.  We can load_parents to get __parent__.

  >>> from ptah.cms import load, load_parents
  >>> load_parents(p)
  [<ptah.cms.root.ApplicationRoot at 0x3df04b0>]
  >>> p.__parent__
  <ptah.cms.root.ApplicationRoot at 0x3df04b0>

As you use the system you will notice that we attempt not to load objects as that can be a expensive operation.  So if an object refers to another object it will do so by URI.  So let's load a object via its URI.

  >>> load(p.__uri__)
  <ptah.cmsapp.content.page.Page at 0x3df16b2>

`load` also supports passing in a Permission which can checked after loading which will raise Forbidden if the user does not have this permission on Content.

sql way
This would only work with leafs not with containers.  If you attempt to do this with a container you will get a ReferentialIntegrity exception from the database.  The CMS will also not be notified instead since there are no events being thrown.

  >>> Session.delete(page)

cms way
This way will always work with either Leafs or Containers.  It will also notify the CMS of events.

  >>> page.delete()


[XXX] We should probably rename Factories as Applications or provide a way
of obtaining Application instances
[XXX] define how you can "load security" e.g. logged in as a user, load(uri) and throw exception