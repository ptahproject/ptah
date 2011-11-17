Ptah Q & A
==========

What is scope of Ptah?
----------------------

Ptah aims to provide a framework which makes low level choices for developers so the programmer can get on with solving their problem on a unrealistic deadline.  It is high level compared to Pyramid but lower level compared to something like Plone or Drupal.  ptah.cms is a API it is not a CMS, it will not have advanced CMS functionality such as staging, workflow or versioning; those will be optional and if support is required in data model we will ensure it is not required and that such features can be optional (e.g. ptah_cms_nodes.parent).

Ptah is a framework, an implementation and set of opinions around the Pyramid web framework.  It supports `URL dispatch`, `Traversal`, a SQL data model, pyramid view-level security, content heirarchy, multiple applications living in the same content heirarchy, a high level security policy (permissions, roles, and principals).

Ptah Manage aims at provide 100% visibility into ALL aspects of your application and how its using the Ptah framework.  Ptah Manage is about transparency of configuration for developers/administrators.  Your App is what you write and solves your customers/end user problems.

Where does Pyramid and Ptah differ?
-----------------------------------

This needs to be fixed.  A lot has changed nad Ptah only adds API and is practical "yet another library" which can be used from any Pyramid application.

In Pyramid you must create a configurator and explicitly include/configure everything.  Ptah has config step which can scan and load all modules on initialization.  So if you have a module which defines a ptah entry-point in your setup.py; it will automatically get loaded.  Any module with a ptah entry-point needs to be excluded for it *not* to be loaded.

Ptah provides a different set of facilities for view, config and settings management.  Everything you know about Pyramid is valid.  In many cases what makes Ptah Manage work the way it does it due to these higher-level subsystems (see Introspection module in Ptah Manage UI).

Anytime Ptah provides a facility that is _like_ Pyramid it is solely for introspection reasons.  You can use all Pyramid API and use Ptah just like a normal Pyramid library; you will just lose `Ptah Manage` features and you may need to take on some extra setup work since Ptah provide convienance.

Will Ptah and Pyramid merge functionality?
------------------------------------------

Probably.  Ptah is very new and once functionality is understood by both communities merging code is good possibility.  Some useful reusable subsystems in Ptah are ptah.view, ptah.config, ptah.config.settings systems.  Not surprsingly Ptah's subsystems are higher level than Pyramids - Ptah started off being an application not a library.

Why does Ptah not use deform?
-----------------------------

Because we do not use colander for form schema.

Why we do not use colander for forms
------------------------------------

Colander is nice general schema language.  We use it for settings management.  In many cases when you are working with forms you want to work logically with a Field (schemanode and widget).  It is the case with colander that responsibilities are separated in which (de)serialization is done with colander and the widget turns that into internal structure for the widget.  If you make your own widget you will need to keep in mind how colander schemas can use your widget and you may end up having to keep a colander schemanode in sync with your widget.  We believe that most people desire a tighter coupling between widget and schema when working with widgets; they would like to see everything in one place.

If you understand colander, ptah.form will be familiar.  After all we sort of forked it and folded it into ptah.form.  The big difference is we have removed some additional flexibility from colander, such as nesting of schema nodes.  ptah.form.fields has both schema and field definition in one class, Field.

Why does Ptah use a Folder paradigm?
------------------------------------

It *does not* require a Folder paradigm or containment.  ptah.cmsapp demonstrates the features of ptah.cms and one of those features are content hierarchies.  Thus the Page/Folder experience in ptah.cmsapp.  We currently have a Poll add-on which does not participate in Page/Folder heirarchy.

Why does Ptah not use ZODB?
---------------------------

We envision a Ptah extension which will allow ZODB developers to work with
the system in a manner familiar with them.  ZODB is for a sophisticated
developer profile which we do not target; so we do not intend to support it
in the core system.  We hope the Ptah community will develop patterns to
integrate object persistence into Ptah.

Why does Ptah not use Mongo?
----------------------------

We envision a Ptah extension which will allow Mongo to be used as a first
class citizen.  Mongo is not transactional and is for a sophisticated
developer profile which we do not target; so we do not intend to support it
in the core system.  We hope the Ptah community will develop patterns to
integrate Mongo into Ptah.

Why does Ptah use sqlite?
-------------------------

Ptah uses SQLAlchemy which supports many different database drivers.  sqlite ships with Python obviating the need to install a separate database daemon.  ptah.cms will not depend on database specific features to gain performance or scalability.  simplicity and approachability are the overriding concerns in Ptah.

Pyramid is not a bottleneck; Ptah is
------------------------------------

Any experienced web developer will tell you that accessing data or going out of process for IO will slow down the responsiveness of the the application.  This is true of Ptah.  That is why we have such few SQL calls in the run-time.  We aim for Ptah *not* to be a bottleneck for your application.  Ptah goes out of its way to do as much as possible at start-up time.  You can see the SQLAlchemy queries per page using the pyramid_debugtoolbar that ships with development profile.

Ptah does not use Jinja, Mako, etc. Why?
----------------------------------------

NOTE: As of early Nov. 2011; you should be able to use any templating
system with Ptah since we have removed our view functionality.  All
views are Pyramid views and thus can use any renderer from pyramid.

We are still debating this.  It is possible to make Ptah not require Chameleon.  The goal is that developers can get an add-on and have it work seamlessly.  Having developers expect to use a single templating engine is reasonable; it reduces the amount of choices they need to make.  Also if they are interested in the add-on functonality they are probably committed to Ptah; so whatever template engine decision Ptah makes - the developer will be willing to accept that decision.

Chameleon is mature, fast, and feature rich.  The two most critized aspects of Chameleon are DOM attirbute markup and METAL.  Building composable applications (applications which use lots of addons) which require accessibility would be quite painful without attirbute markup.  METAL is Chameleon's template composition machinery; it is advanced and confusing.  That is why Ptah's view machinery provides a layout concept so programmers do not have to use METAL (unless they choose) and we feel it makes template composition more explicit and more easily understood.

Ptah Manage isnt as Powerful as Django Admin
--------------------------------------------

The Ptah Manage facility is not meant to be a extension point for end users.  It is meant for developers and/or systems administrators to use.  Your application is what we assume would be useful for end users to interact with and that is why it exists.  You may see similarities between the two "Admin" systems but really the only aspect which is comparable is the SQLAlchemy introspection mechanism in Ptah Manage.  Which is really meant for quick and dirty review/edits of raw data.   Remember manipulating data through SQLAlchemy module in Ptah Manage does *not* notify the application of the event; so subscribers in the application will not be able to react to such data changes.

SQLAlchemy is Complex and Scary
-------------------------------

SQLAlchemy is a comprehensive library and an effect of that is it can feel overwhelming when reviewing the documentation.  You do not need to understand SQLAlchemy deeply is use Ptah.  The models that you write will most likely be simple and you will need to add behavior to them.  We believe 99% of developers will never have to learn anything "deep".

SQLAlchemy also has books written on it and is ported to Python 3.  There is a large friendly user community that is willing to answer questions.  It is a solid foundation to build on top.

See content.rst for example of SQLAlchemy usage.

Why do you say REST is First Class?
---------------------------------------------------

If your content model inherients from ptah.cms.Content than it will automatically be exposed via the Ptah REST API.  You will be able to update and call REST Actions on your models over REST.  We say its first class because the framework treat REST as important as it does its SQL data model.  You will always have a JSON representation of your model.

Ptah doesnt work in my browser
------------------------------

As of this writing we have not started pushing the boundaries of HTML5.  We expect release of Ptah to not work in browsers without HTML5 support.  Ptah is aiming for web browsers IE9/10 and latest Firefox, Chrome and Safari as of end of 2011.  If your browser does not work - you can read the documentation and customize the templates to work with your or your customers browsers.

Backwards compatibility (especially regarding browsers) is a non-priority for Ptah.  We are aiming to support current and future browser standards not standards we have had foisted upon us as of today.

Ptah cheats and uses SQL like NoSQL
-----------------------------------

The core ptah.cms data model is very simple and meant to be extensible.
We do store JSON for some attributes (like security) instead of separate tables for performance and convienance reasons.  Ptah isnt a academic
exercise it is to help people get work done efficiently.  The core data
model is simple enough that you can normalize your schema's however you
like but that doesnt mean the core system needs to have that complexity.
The other "cheat" is that we store path in the content table.  This enables
fast lookups if using content hierarchies (1 simple SELECT).  ptah.cms
has 3 tables and one of them (ptah_cms_content) is not required to be used
unless you want heriarchies.

The data model is simple and modern.  It isnt cheating.  It is practical.

Another note on the ptah_cms_content.path column is that many people have
tried and failed to have "pure" heriarchies in SQL (Ars Digita) and if you
go down that road you will end up having to specialize around a particular
database (Oracle or Postgresql - most likely).  We can do that in an
extension to Ptah but not in the core framework.  The core framework must be database agnostic, simple, comprehensible, and fast.  So we make containment an application concern and the problem becomes much simpler.

I hate traversal, why would I use Ptah?
---------------------------------------

You do not need to use traversal/containment with Ptah.  You can still use nearly all of ptah.cms.  Containment is useful concept and it is how many users think about website management.  After all Apache uses containment; just instead of a database it uses a filesystem.

