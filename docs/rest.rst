REST
====

REST is first class citizen in Ptah.  If you use the Content model then you get
REST for free.  If you want 'low-level' Node interface you need to do more work.
The follow relies on Ptah App.

You will need curl and ptah running for this example.

Overview
--------
REST API is flat.  If your content participates in heirarchy the system will
take this into account when computing security.

Note that in the following values for __link__, __uri__ will be different in
than what you will see.  You can figure this out.  For clarity we just use data
available from our session.

Also to note there is a ptahclient.py and a rest.py which support programatic
usage of the REST API from python.  You do not need to use cURL.  We just use it
for these examples.

Basics
------

Quick look at out-of-the-box REST::

  $ curl http://localhost:8080/__rest__/cms/
    {
     "name": "cms",
     "link": "http://localhost:8080/__rest__/cms/",
     "title": "Ptah CMS API",
     "description": "",
     "actions": [
      {
       "name": "apidoc",
       "link": "http://localhost:8080/__rest__/cms/apidoc",
       "title": "API Doc",
       "description": ""
      },
      {
       "name": "content",
       "link": "http://localhost:8080/__rest__/cms/content",
       "title": "CMS content",
       "description": ""
      },
      {
       "name": "applications",
       "link": "http://localhost:8080/__rest__/cms/applications",
       "title": "List applications",
       "description": ""
      },
      {
       "name": "types",
       "link": "http://localhost:8080/__rest__/cms/types",
       "title": "List content types",
       "description": ""
      }
     ]
    }

This is the default REST view for the cms, it is the `apidoc` view.  More
information will describe why but once you understand more about REST this will
become clear.  To be clear::

  $ curl http://localhost:8080/__rest__/cms/
  .. output
  is the same as
  $ curl http://localhost:8080/__rest__/cms/apidoc/

Let's look at applications, currently there are quite a few since we are
experimenting with multiple applications and mount points. But for this example
we are only interested in an application whose __mount__ is '' (the default).
This is the same application served at http://localhost:8080/ - back to code::

  $ curl http://localhost:8080/__rest__/cms/applications
    [
     {
      "__type__": "cms+type:app",
      "__content__": true,
      "__uri__": "cms+app:c24d0e245edc413980a75f035ee3c8b2",
      "__parents__": [],
      "__name__": "root",
      "__container__": true,
      "title": "Ptah CMS",
      "description": "",
      "view": "",
      "created": "2011-10-12T04:04:08.550000",
      "modified": "2011-10-12T04:04:08.550000",
      "effective": null,
      "expires": null,
      "__mount__": "",
      "__link__": "http://localhost:8080/__rest__/cms/content:/cms+app:c24d0e245edc4
    13980a75f035ee3c8b2/"
     }
    ]

Now lets see the application.  Note in future the default will not show children
since that will not work for large containers and will need batching support.
Let's just see how it is today::

  $ curl http://localhost:8080/__rest__/cms/content:/cms+app:c24d0e245edc413980a75f035ee3c8b2/

    {
     "__type__": "cms+type:app",
     "__content__": true,
     "__uri__": "cms+app:c24d0e245edc413980a75f035ee3c8b2",
     "__parents__": [],
     "__name__": "root",
     "__container__": true,
     "title": "Ptah CMS",
     "description": "",
     "view": "",
     "created": "2011-10-12T04:04:08.550000",
     "modified": "2011-10-12T04:04:08.550000",
     "effective": null,
     "expires": null,
     "__link__": "http://localhost:8080/__rest__/cms/content:/cms+app:c24d0e245edc41
    3980a75f035ee3c8b2/",
     "__contents__": [
      {
       "__name__": "front-page",
       "__type__": "cms+type:page",
       "__uri__": "cms+page:b4d90058672a4c11991dd5eb11b118fd",
       "__container__": false,
       "__link__": "http://localhost:8080/__rest__/cms/content:/cms+page:b4d90058672
    a4c11991dd5eb11b118fd/",
       "title": "Welcome to Ptah",
       "description": "",
       "created": "2011-10-12T04:04:08.557000",
       "modified": "2011-10-12T04:04:08.557000"
      },
      {
       "__name__": "folder",
       "__type__": "cms+type:folder",
       "__uri__": "cms+folder:f396f8fe8a684b62b11c90c3e6bb09ba",
       "__container__": true,
       "__link__": "http://localhost:8080/__rest__/cms/content:/cms+folder:f396f8fe8
    a684b62b11c90c3e6bb09ba/",
       "title": "Test folder",
       "description": "",
       "created": "2011-10-12T04:04:08.559000",
       "modified": "2011-10-12T04:04:08.559000"
      }
     ]
    }

Lets look at the apidoc for the application.  These are the REST actions that are
available.  By default Anonymous can create a Page, therefore create is an
available action (recognized its not a sensible default and will be changed in future)::

    $ curl http://localhost:8080/__rest__/cms/content:/cms+app:c24d0e245edc413980a75f035ee3c8b2/apidoc
    [
     {
      "name": "info",
      "link": "http://localhost:8080/__rest__/cms/content:/cms+app:c24d0e245edc41398
    0a75f035ee3c8b2/",
      "title": "",
      "description": "Container information"
     },
     {
      "name": "apidoc",
      "link": "http://localhost:8080/__rest__/cms/content:/cms+app:c24d0e245edc41398
    0a75f035ee3c8b2/apidoc",
      "title": "apidoc",
      "description": "api doc"
     },
     {
      "name": "create",
      "link": "http://localhost:8080/__rest__/cms/content:/cms+app:c24d0e245edc41398
    0a75f035ee3c8b2/create",
      "title": "create",
      "description": "Create content"
     }
    ]


Login
-----

To login via REST you need to get a AUTH-TOKEN, we do this by issueing a GET::

    $ curl -d "login=admin&password=12345" http://localhost:8080/__rest__/login
    {
     "auth-token": "3b0ccaac40e16f2e74c7d00b2c5b2f0e4e95a5beuser%2Bcrowd%3A9a529386a
    61c4f20a2481da6a9f455cc",
     "message": ""
     }

Now that we have the auth-token we will need to pass this as a HTTP HEADER, X-AUTH-TOKEN::

    $ curl -H "X_AUTH_TOKEN:3b0ccaac40e16f2e74c7d00b2c5b2f0e4e95a5beuser%2Bcrowd%3A9a529386a
    61c4f20a2481da6a9f455cc" http://localhost:8080/__rest__/cms/

This request is an authenticated request to Ptah with the admin user. Currently
you will not see any difference but this will change. Let's see it with apidoc.

Authenticated Example
---------------------

Content actions can be protected by permissions. Let us presume that our CMS
root's __uri__ is `cms+app:c24d0e245edc413980a75f035ee3c8b2` and it's __link__ is
`http://localhost:8080/__rest__/cms/content:/cms+app:c24d0e245edc413980a75f035ee3c8b2/`
.  Let's look at APIDOC not logged in::

    $ curl http://localhost:8080/__rest__/cms/content:/cms+app:c24d0e245edc413980a75f035ee3c8b2/apidoc

    [
     {
      "name": "info",
      "link": "http://localhost:8080/__rest__/cms/content:/cms+app:c24d0e245edc413980a75f035ee3c8b2/",
      "title": "",
      "description": "Container information"
     },
     {
      "name": "apidoc",
      "link": "http://localhost:8080/__rest__/cms/content:/cms+app:c24d0e245edc413980a75f035ee3c8b2/apidoc",
      "title": "apidoc",
      "description": "api doc"
     },
     {
      "name": "create",
      "link": "http://localhost:8080/__rest__/cms/content:/cms+app:c24d0e245edc413980a75f035ee3c8b2/create",
      "title": "create",
      "description": "Create content"
     }
    ]

Now let's look at APIDOC as a logged in user::

    $ curl -H "X_AUTH_TOKEN:8725da7fdf14e1442f1ed4670f3b61614e95a6bcuser%2Bcrowd%3A9a529386a61c4f20a2481da6a9f455cc" \
      http://localhost:8080/__rest__/cms/content:/cms+app:c24d0e245edc413980a75f035ee3c8b2/apidoc

    [
     {
      "name": "info",
      "link": "http://localhost:8080/__rest__/cms/content:/cms+app:c24d0e245edc413980a75f035ee3c8b2/",
      "title": "",
      "description": "Container information"
     },
     {
      "name": "apidoc",
      "link": "http://localhost:8080/__rest__/cms/content:/cms+app:c24d0e245edc413980a75f035ee3c8b2/apidoc",
      "title": "apidoc",
      "description": "api doc"
     },
     {
      "name": "create",
      "link": "http://localhost:8080/__rest__/cms/content:/cms+app:c24d0e245edc413980a75f035ee3c8b2/create",
      "title": "create",
      "description": "Create content"
     },
     {
      "name": "delete",
      "link": "http://localhost:8080/__rest__/cms/content:/cms+app:c24d0e245edc413980a75f035ee3c8b2/delete",
      "title": "delete",
      "description": "Delete content"
     },
     {
      "name": "move",
      "link": "http://localhost:8080/__rest__/cms/content:/cms+app:c24d0e245edc41398
      "title": "move",
      "description": "Move content"
     },
     {
      "name": "update",
      "link": "http://localhost:8080/__rest__/cms/content:/cms+app:c24d0e245edc413980a75f035ee3c8b2/update",
      "title": "update",
      "description": "Update content"
     }
    ]

Available Types
---------------

We can see a list of all available types available in the system.  The `Type`
information contains:

   * __uri__, this is a resolvable string which is unique to the type information

   * name, this is the internal type name which does not have to be unique

   * title, human readable title of the type information

   * permission, permission to create models of this type

   * fieldset, schema of the type. if you do not define one the system
     will create one by introspecting your model.

Let's see all registered types::

    $ curl http://localhost:8080/__rest__/cms/types/
    [
     {
      "__uri__": "cms+type:app",
      "name": "app",
      "title": "Application",
      "description": "",
      "permission": "__not_allowed__",
      "fieldset": [
       {
        "type": "text",
        "name": "title",
        "title": "Title",
        "description": "",
        "required": true
       },
       {
        "type": "textarea",
        "name": "description",
        "title": "Description",
        "description": "",
        "required": false
       }
      ]
     },
     {
      "__uri__": "cms+type:file",
      "name": "file",
      "title": "File",
      "description": "A file in the site.",
      "permission": "ptah-app: Add file",
      "fieldset": [
       {
        "type": "text",
        "name": "title",
        "title": "Title",
        "description": "",
        "required": true
       },
       {
        "type": "textarea",
        "name": "description",
        "title": "Description",
        "description": "",
        "required": false
       },
       {
        "type": "file",
        "name": "blobref",
        "title": "Data",
        "description": "",
        "required": true
       }
      ]
     },
     {
      "__uri__": "cms+type:folder",
      "name": "folder",
      "title": "Folder",
      "description": "A folder which can contain other items.",
      "permission": "ptah-app: Add folder",
      "fieldset": [
       {
        "type": "text",
        "name": "title",
        "title": "Title",
        "description": "",
        "required": true
       },
       {
        "type": "textarea",
        "name": "description",
        "title": "Description",
        "description": "",
        "required": false
       }
      ]
     },
     {
      "__uri__": "cms+type:page",
      "name": "page",
      "title": "Page",
      "description": "A page in the site.",
      "permission": "ptah-app: Add page",
      "fieldset": [
       {
        "type": "text",
        "name": "title",
        "title": "Title",
        "description": "",
        "required": true
       },
       {
        "type": "textarea",
        "name": "description",
        "title": "Description",
        "description": "",
        "required": false
       },
       {
        "type": "tinymce",
        "name": "text",
        "title": "Text",
        "description": "",
        "required": true
       }
      ]
     }
    ]



Create content
--------------

Let us create a Page whose name is 'foobar.html'.

There is a special feature of `container.create REST action` which allow you to create type
and update all values in one operation. Here is example of creating ptah.cmsapp.content.Page::

    $ curl -H "X_AUTH_TOKEN:8725da7fdf14e1442f1ed4670f3b61614e95a6bcuser%2Bcrowd%3A9a529386a61c4f20a2481da6a9f455cc" \
      --url "http://localhost:8080/__rest__/cms/content:/cms+app:c24d0e245edc413980a75D5D5f035ee3c8b2/create?tinfo=cms+type:page&name=foobar.html"
    {
     "message": "cms+page:032e6b19a99c40fba264c1aeeaf08254"
    }

`tinfo` is the type's __uri__.  You can get a list of available types by
querying __rest__/cms/types for instance, the default types available with ptah.cmsapp are:

   - cms+type:page
   - cms+type:folder
   - cms+type:file

The response of the message is the new URI for the content item. Let's just CURL
the item::

    $ curl http://localhost:8080/__rest__/cms/content:/cms+page:032e6b19a99c40fba264c1aeeaf08254
    {
     "__type__": "cms+type:page",
     "__content__": true,
     "__uri__": "cms+page:032e6b19a99c40fba264c1aeeaf08254",
     "__parents__": [
      "cms+app:c24d0e245edc413980a75f035ee3c8b2"
     ],
     "__name__": "foobar.html",
     "__container__": false,
     "title": "",
     "description": "",
     "text": "",
     "view": "",
     "created": "2011-10-12T14:44:01.640000",
     "modified": "2011-10-12T14:44:02.669000",
     "effective": null,
     "expires": null,
     "__link__": "http://localhost:8080/__rest__/cms/content:/cms+page:032e6b19a99c40fba264c1aeeaf08254/"
    }

Python REST Client
------------------

Two files are of interst.  devapp/ptahclient.py which is a python REST client for
Ptah. And rest.py which utilizes ptahclient.py.
