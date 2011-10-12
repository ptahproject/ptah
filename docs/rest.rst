REST
====

REST is first class citizen in Ptah.  If you use the Content model then you get REST for free.  If you want 'low-level' Node interface you need to do more work.   

You will need curl and ptah running for this example.

Overview
--------
REST API is flat and not heirarchical.  It does take content heirarchy into consideration when computing security.  But the API is flat.  Twillio & github are inspirations.

Note that all __link__, __uri__ will change based on data in the database.  identifiers in this example will not match with yours.  We presume you can figure this out.  For clarity we just use data available from our session.  

Also to note there is a ptahclient.py and a rest.py which support programatic usage of the REST API from python.  You do not need to fiddle with cURL ;-)  We just use it for these examples.

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

This is the default REST view for the cms, it is the `apidoc` view.  More information will describe why but once you understand more about REST this will become clear.  To be clear::

  $ curl http://localhost:8080/__rest__/cms/
  .. output
  is the same as 
  $ curl http://localhost:8080/__rest__/cms/apidoc/

Let's look at applications, currently there are quite a few since we are experimenting with multiple applications and mount points.  But for this example we are only interested in an application whose __mount__ is '' (the default).  This is the same application served at http://localhost:8080/ - back to code::

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

Now lets see the application.  Note in future the default will not show children since that will not work for large containers and will need batching support.  Let's just see how it is today::

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

Lets look at the apidoc for the application.  These are the REST actions that are available.  By default Anonymous can create a Page, therefore create is an action::

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

To login via REST you need to get a AUTH-TOKEN, we do this by doing FORM Post with curl.

    $ curl -d "login=admin&password=12345" http://localhost:8080/__rest__/login
    {
     "auth-token": "3b0ccaac40e16f2e74c7d00b2c5b2f0e4e95a5beuser%2Bcrowd%3A9a529386a
    61c4f20a2481da6a9f455cc",
     "message": ""
     }

Now that we have the auth-token we will need to pass this as a HTTP HEADER, X-AUTH-TOKEN::

    $ curl -H "X_AUTH_TOKEN:3b0ccaac40e16f2e74c7d00b2c5b2f0e4e95a5beuser%2Bcrowd%3A9a529386a
    61c4f20a2481da6a9f455cc" http://localhost:8080/__rest__/cms/

This request is an authenticated request to Ptah with the admin user.  Currently you will not see any difference but this will change.  Let's see it with apidoc.

Authenticated Example
---------------------

Content actions can be protected by permissions.  Let us presume that our CMS root's __uri__ is `cms+app:c24d0e245edc413980a75f035ee3c8b2` and it's __link__ is `http://localhost:8080/__rest__/cms/content:/cms+app:c24d0e245edc413980a75f035ee3c8b2/`
.  Let's look at APIDOC not logged in::

    $ curl http://localhost:8080/__rest__/cms/content:/cms+app:c24d0e245edc413980a7
5f035ee3c8b2/apidoc
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

Now let's look at APIDOC as a logged in user.

$ curl -H "X_AUTH_TOKEN:8725da7fdf14e1442f1ed4670f3b61614e95a6bcuser%2Bcrowd%3A
9a529386a61c4f20a2481da6a9f455cc" http://localhost:8080/__rest__/cms/content:/c
ms+app:c24d0e245edc413980a75f035ee3c8b2/apidoc
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
 },
 {
  "name": "delete",
  "link": "http://localhost:8080/__rest__/cms/content:/cms+app:c24d0e245edc41398
0a75f035ee3c8b2/delete",
  "title": "delete",
  "description": "Delete content"
 },
 {
  "name": "move",
  "link": "http://localhost:8080/__rest__/cms/content:/cms+app:c24d0e245edc41398
0a75f035ee3c8b2/move",
  "title": "move",
  "description": "Move content"
 },
 {
  "name": "update",
  "link": "http://localhost:8080/__rest__/cms/content:/cms+app:c24d0e245edc41398
0a75f035ee3c8b2/update",
  "title": "update",
  "description": "Update content"
 }
]

Create content
--------------

Let us create a Page whose name is 'foobar.html'.  Create 

There is a special feature of `container.create REST action` which allow you to create type and update all values in one operation.  

    $ curl -H "X_AUTH_TOKEN:8725da7fdf14e14
    42f1ed4670f3b61614e95a6bcuser%2Bcrowd%3A9a529386a61c4f20a2481da6a9f455cc" --url
     "http://localhost:8080/__rest__/cms/content:/cms+app:c24d0e245edc413980a75D5D5
    f035ee3c8b2/create?tinfo=cms+type:page&name=foobar.html"
    {
     "message": "cms+page:032e6b19a99c40fba264c1aeeaf08254"
    }

The response of the message is the new URI for the content item.  Let's just CURL the item.

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
     "__link__": "http://localhost:8080/__rest__/cms/content:/cms+page:032e6b19a99c4
    0fba264c1aeeaf08254/"
    }