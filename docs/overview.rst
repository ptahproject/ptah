=========
Why Ptah?
=========

Because at Enfold Systems we build complicated systems for customers with a
fixed price or need to estimate a relatively accurate cost for project
completion.  Customers are asking for interactive features which require
a lot of javascript (e.g. REST representations of models).  Many of our
customers care deeply about security and work inside of discrete groups
among themselves.  Therefore we needed a model which provided relatively
fine-grain security in the framework.  Our projects use other open source
communities code to do work.  We want to facilitate sharing addons with
this framework so we can solve our customers requirements with less effort.
Lastly Pyramid appealed to us because of its documentation, test coverage,
and attention to API design.

=============
What is Ptah?
=============

Ptah is a Python based web development framework whose goal is to allow
developers to more predictably develop complex web applications.  Ptah
is cross platform and runs on Windows, OSX and Linux.  Ptah is built on
top of the Pyramid framework and lets Pyramid do most of the heavy lifting.
Ptah uses SQLAlchemy for relational database abstraction/connectivity.
Ptah runs on Python 2.7 and will soon run on Python 3.2.

Ptah is also the Egyptian god of craftsmanship.  He built the sky.

========
Ptah CMS
========

The ptah.cms package depends on the ptah package and contains no policy or
user interface.  The pixels you see on the screen resulting from the
:doc:`install` document is ptah.cmsapp.  The kernel of the CMS exists in ptah.cms.
If you want an alternative datastore, fork the ptah.cms package and change the
models to use mongo, zodb, etc.

The package is responsible for permissions, base content models, blob storage,
REST representation of models, "type" information (abstraction on concrete
content/data model), and application concept, as well as a traverser which
integrates a URL (you pick where) with the efficient lookup, security,
and dispatch based on URL.

If you want an example of using ``ptah.cms``, look at ``ptah.cmsapp``, which
contains implementation of the CMS types, such as File, Folder and Page.
This package is will probably not be useful unless you want to write a CMS
with your own opinions.

============
Applications
============

In your URL you will have one or more applications which participate in Ptah.
If you want Ptah to be invoked at the root of your site, you will define an
application as /.  This application will have a database record associated with
it.  Also you may want to specify a security policy to be applied to this
application (for instance, allowing authenticated users to create a Page but
not having ability to create Files or Folders.)  In some systems the
application designer will want to apply security policies based on the URL
structure.  One way of accomplishing this is wiring Applications into your
URL structure.

ApplicationFactory
==================

The ApplicationFactory determines where in your URL you want the CMS to define
an ApplicationRoot.  An ApplicationFactory is *not* persistent.  For instance,
if you have a existing URL structure but want to apply a application-level
policy (such as different theme, security, workflow or other feature), the
ApplicationFactory is the mechanism to use.

ApplicationFactory is a start-up time configuration which specifies
a place in your URL to define where you want to mount an Application.
You must have at least one ApplicationFactory call or else you will be unable
to use the CMS.  The ApplicationFactory will return the ApplicationRoot based
on where you `mount` the Application into your heirarchy.

  e.g.::

    factory = ptah.cms.ApplicationFactory('/', 'root', 'Ptah CMS')
    ptah.config.add_route('root-app', '/*traverse',
        factory = factory, use_global_views = True)

This means / will be an ApplicationRoot with the identifier ``root-app``.
If you go to ``http://host/path/to/content`` and there is no other pyramid
route which defines ``/path/to/content``, Pyramid will invoke the Ptah traverser
using the ApplicationRoot located at ``/`` to look up content.

In summary, the ApplicationFactory collaborates with Pyramid to invoke an
ApplicationRoot object in your URL hierarchy.

Characteristics

  * Required: Yes
  * Runtime configurable: No
  * Persistent: No

ApplicationRoot
===============

An ApplicationRoot is persistent CMS `container` which is addressable by
URL.  It is a concrete model which has a ``Type`` attribute of `Application`.
It is responsible for computing the URLs for a given resource or model which
is contained in the ApplicationRoot.  The depth of model descendants may be
arbitrary but can be overridden by another ApplicationRoot further down the
URL structure.

   You must have at least 1 ApplicationRoot object in the Ptah CMS.

Characteristics

  * Required: Yes
  * Runtime configurable: No
  * Persistent: No

ApplicationPolicy
=================

ApplicationFactory may take a policy argument, ApplicationPolicy.
An ApplicationPolicy currently only provides a `security policy` for the
ApplicationFactory.  This is very useful feature if you need to alter your
security model at an `ApplicationRoot` but you want such a change to be
isolated to the container and applied to all descendants.

Characteristics

  * Required: Yes
  * Runtime configurable: No
  * Persistent: No

Content, Hierarchy

Traverser
=========

The ContentTraverser is bound to the ApplicationRoot and registers itself
with Pyramid.  So if Pyramid resolves URL into an ApplicationRoot it will
use this custom traverser.  A traverser is responsible for resolving the URL
into a response by pyramid.  :py:class:`ptah.cms.Traverser`
will lookup the location of the model via the `ptah_cms_content` table.

Traversal is only used for the content hierarchy.  URL Dispatch can still
be used to participate in CMS facilities, such as REST and Security.

Characteristics

  * Required: Yes
  * Runtime configurable: No
  * Persistent: No

TypeInformation and Actions
===========================

The type/action classes enable you to describe your model and
application "actions" at an application level.  For instance,
what URL you will need to go to in the browser to generate an Edit screen
and what permission you will need to Add, Edit or Delete a model are
examples of information you pass in via the `Type` class.  The ``Action``
class is used to specify what URLs a user or REST API will be exposed to the
end user to perform some work.  The most common example of usage is determining
what the ``AddForm`` URL is for a given Type.

Type

    `type` name is registered with all ptah_cms_node but is not required.  So
    while the Type information is not persisted, the type ``name`` is
    in the database.  If you change the Type name, you will need
    to update database records using the Type information.

    Characteristics

      * Required: No
      * Runtime configurable: Yes
      * Persistent: Yes

Action

    Characteristics

      * Required: No
      * Runtime configurable: Yes
      * Persistent: No

Node and Content
================

The  persistent data model for Ptah CMS revolves around the following 3 tables.
You can pick and choose which level of integration you want, but there are some
ramifications of which you should be aware so future extension is easier.

Ptah attempts to NOT pollute the model namespace with internal implementation
details.  Therefore things such as id, uri, type, parent, path, etc.  will not
be available on the model with such names.  We have referenced them separately which
does mean you need to know the `SQLAlchemy Entity Property` when querying,
filtering, ordering by these properties.  This *does* mean you are free to use
id, uri, type, parent, etc. on your OWN models without concerns that you are
conflicting with Ptah.

Node
~~~~

:py:class:`ptah.cms.node.Node` is the primary table.  Columns for the
``ptah_cms_nodes`` table:

id
   Primary key which is an internal implementation detail for SQLAlchemy.

   SQLAlchemy Entity property: ``__id__``
   Database column name: ``id``

uri
   A required unique string which is used throughout the system to refer to
   the record.  A common pattern is to use URI to reference models instead of
   their primary key.  An example, blob+sql:9f4b24205c704dbc99a24abdd2f55350

   SQLAlchemy Entity property: ``__uuid__``

   Database column name: ``ptah_cms_nodes.uri`` (VARCHAR)

type
   This is the application-level "type" information which provides a
   indirection for model re-use. A News Item is a Page with a different
   :py:class:`ptah.cms.tinfo.TypeInformation`.

parent
   A UUID of the parent.  The only time this will be null is in the
   ApplicationRoot in /.  For instance, a Page's parent attribute will be
   its container's UUID.

owner
   Owner is the URI of a Principal URI.
   This field gets set by the subscriber for :py:class:`ptah.cms.events.ContentCreatedEvent`
   An example, user+crowd:301067f19db649098d51659a8b8aa572

roles
   A :py:class:`ptah.utils.JSONType` which will contain which roles have custom permissions.
   A node with the following data would give Principal the manager role::

     {u'user+crowd:301067f19db649098d51659a8b8aa572': [u'role:manager']}

acls
   A :py:class:`ptah.utils.JSONType` which will contain a sequence of named ACL maps.

Content
~~~~~~~

``ptah_cms_content`` is an optional application-level data model which
provides high level attributes core to ``ptah.cms`` as well as some
optimization information.  for instance, there is a `path` column
which we use to fast-path lookups for leaf nodes in `traversal`.

path
    The internal path representation of the URL used to efficiently
    traverse a pyramid URL into the internal data model.  For instance:
    a Page which is located at http://host/folder/front-page will be
    internally represented as, /${ptah.cms.node.uuid}/folder/front-page

    e.g. /cms+app:f4642bf9d7cb42fb92578763b4dc91aa/folder/front-page/

name
    A unique name in the ``ptah_cms_nodes.parent`` container.  this
    is primary used for traversal.  not required for url_routing or
    security.

title
    CMS title attribute. self explanatory.

description
    CMS description attribute, self explanatory.

view
    A URI string which can be resolved via the :py:func:`ptah.uri.resolve`
    function. In the traditional CMS UI sense, you can default a Folder to have
    a Page as the view.  Anything that can be resolved can be a "view" for a
    content item.

    Rules for view resolution:
      - ptah_cms_content.view
      - traversal

created
    Datetime to mark when the record was created.

modified

    Datetime to mark when the record was last modified, in UTC

effective

    Datetime to mark when the record should be visible or "effective".
    DublinCore attribute in UTC.

expires

    Datetime to mark when record should no longer be visible in the CMS.
    DublinCore attribute in UTC.

creators

    A JsonType sequence of principal URIs which are able to be resolved.
    Any number of creators may be assigned to a piece of content.  Often
    anyone involved in the editorial process may be assigned.

subjects

    Jsontype?

publisher

    DublinCore attribute. Unicode.

contributors

    DublinCore attribute. JsonType sequence of URIs.

Container
~~~~~~~~~

There is no data model/persistent difference between Content and Container.
The database records are identical.  The difference is the :py:class:`ptah.cms.Container`
model supports a Mapping-like interface so you can resolve children efficiently.
It also makes it easier for programmers to model/manipulate containment relationships.

This API is added for conveniance but is a natural way of interacting with the
hiearchy. For example, if you have a piece of content, (say, 'front-page') in a
Folder, how can you delete it?

Using low-level SQLAlchemy without application events::

  from ptah.cms import Session, Content
  page = Session.query(Content).filter_by(Content.__name__='front-page').all()[0]
  Session.delete(page)
  import transaction; transaction.commit()

If you delete a page going directly through the ORM; Ptah will not catch events.

Using high-level Ptah data access::

  from ptah.cms import Session, Content
  page = Session.query(Content).filter_by(Content.__name__='front-page').all()[0]
  page.delete()
  import transaction; transaction.commit()

There are several other approaches.  One could be del container['page.html']

URIs
====

In Ptah all models have a URI in the form ``scheme:UID``. For example::

      >> from ptah.cms import Session, Node
      >> x.__uri__ for x in Session.query(Node).all()]
      [u'cms+app:f4642bf9d7cb42fb92578763b4dc91aa',
       u'cms+page:0d60fc5c2128449898a92a90fa757173',
       u'cms+folder:326388ba897843ffbb9cf8fa824ac154',
       u'cms+page:a0b87c1d3f354183bafb3da5a94a097f']

For instance, the default User/Properties system is `ptah-crowd:$UID` for
a user.  And for ptah.cms.ApplicationRoot it is `ptah-app:$UID`.

URI resolution is a core facility and contract of the system. Given any
UUID, the application should be able to load the corresponding model.  This
loose coupling allows for us to store records externally to the system.

At certain times, Ptah may only have a UUID and need to resolve a Model. This is
done by registering a URI resolver.  We do this so we can load a record.

An example::

  >> from ptah.uri import register_uri_resolver
  >> register_uri_resolver('mycustom+record', custom_record_resolver)

Your custom models will need to supply a UUIDGenerator. A
default implementation exists in ptah.uri.UUIDGenerator.  On your models,
you will assign this as __uuid_generator__ = MyCustomUUIDGenerator, which
will produce a URI in your URI scheme, 'mycustom+record:some_unique_string'.

To have a ``ptah_cms_nodes`` record entry, the only requirements are you have
a primary key (which is auto-filled upon INSERT) and a UUID.  A UUID can be
anything you would like, but there is one very minor API you need to satisfy
if you come up with your own $UUID scheme.

Content vs. Container
=====================

In object/graph databases, by the time you resolve a leaf node you will have
already loaded all of the parents.  This is *not* the case in a RDBMS system
such as Ptah.  There are pros and cons to Ptah's approach.  The positive is
that you can efficiently load a record in one query without loading parents.
The con is that we will have loaded only leaf node without its parent and
lineage up the tree to the ApplicationRoot.  While this is obvious if you have
object/graph database background, it is an important concept to understand
since we are working with hierachies.

  See :py:class:`ptah.cms.load_parents`

Security, Lineage, URL Dispatch
===============================

Since the ApplicationPolicy defines ACLs for an ApplicationRoot, which
contains your data model, it will be required for us to use ``load_parents`` to
walk __parent__ until we reach the ApplicationRoot; then we will have all
security roles to satisfy the Pyramid authorization security model.

The fact is you *do not* need to use ``load_parents`` every single time to
aggregate security settings.  You only need this in ad-hoc security delegation
applications in which users can assign Roles to other users on Content.  While
this model is standard in hierarchical/collaboration systems, it is not
particularly useful for many types of applications.

See How-to Ptah with URL Dispatch.

Events
======

See API.
