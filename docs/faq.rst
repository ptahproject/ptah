Ptah Q & A
==========

What is scope of Ptah?
----------------------

Ptah aims to provide a framework which makes low level choices for developers so the programmer can get on with solving their problem on a unrealistic deadline.  It is high level compared to Pyramid but lower level compared to something like Plone or Drupal.  ptah_cms will never require developers to have to participate in advanced CMS functionality such as staging, workflow or versioning; those will be optional and if support is required in data model we will ensure it is not required and that such features can be nullable (like ptah_cms_nodes.parent; its optional).

Ptah is a framework, implementation and set of opinions around the Pyramid web framework.  It supports `URL dispatch`, `Traversal`, a SQL data model, pyramid view-level security, view/template composition system (which can use traversal), content heirarchy, multiple applications living in the same content heirarchy, a high level security policy (permissions, roles, and principals).  Ptah ships as two separate applications, `Ptah Manage` (inside ptah) and `Ptah App`, ptah_app.  

Ptah Manage aims at provide 100% visibility into ALL aspects of your application and how its using the Ptah framework.  Ptah Manage is about transparency of configuration for developers/administrators.  Ptah App is about application developers and end users.  

Where does Pyramid and Ptah differ?
-----------------------------------

Ptah has a view system built on top of Pyramid.
Ptah has a config system that plays nicely with Pyramid.

In Pyramid you must create a configurator and explicitly include/configure everything.  Ptah has config step which can scan and load all modules on initialization.  So if you have a module which defines a memphis entry-point in your setup.py; it will automatically get loaded.  Any module with a memphis entry-point needs to be excluded for it *not* to be loaded.

Ptah provides a different set of facilities for view, config and settings management.  Everything you know about Pyramid is valid.  In many cases what makes Ptah Manage work the way it does it due to these higher-level subsystems (see Introspection module in Ptah Manage UI).

Anytime Ptah provides a facility that is _like_ Pyramid it is solely for introspection reasons.  You can use all Pyramid API and use Ptah just like a normal Pyramid library; you will just lose `Ptah Manage` features and you may need to take on some extra setup work since Ptah provide convienance.

Will Ptah and Pyramid merge functionality?
------------------------------------------

Probably.  Ptah is very new and once functionality is understood by both communities merging code is good possibility.  Some useful reusable subsystems in Ptah are memphis.view, memphis.config, memphis.settings systems.  Not surprsingly Ptah's subsystems are higher level than Pyramids.

Why does Ptah not use deform?
-----------------------------

It's too decomposed for our taste.  memphis.form is simpler and most importantly it will work with our add-on story.  We want fields and widgets to be redistributable.  We believe memphis.form can support this story more easily than deform.

Why does Ptah not use colander?
-------------------------------

We *do* use colander inside of memphis.settings.  At one point, memphis.form *did* use colander.  We felt it added too much complexity to the API.  Ptah strives for API simplicity at all costs.

Why does Ptah use a Folder paradigm?
------------------------------------

It *does not* require a Folder paradigm or containment.  ptah_app demonstrates the features of ptah_cms and one of those features are content heirarchies.  Thus the Page/Folder experience in ptah_app.  We currently have a Poll add-on which does not participate in Page/Folder heirarchy.

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

Ptah uses SQLAlchemy which supports many different database drivers.  sqlite ships with Python obviating the need to install a separate database daemon.  ptah_cms will not depend on database specific features to gain performance or scalability.  simplicity and approachability are the overriding concerns in Ptah.

Pyramid is not a bottleneck; Ptah is
------------------------------------

Any experienced web developer will tell you that accessing data or going out of process for IO will slow down the responsiveness of the the application.  This is true of Ptah.  That is why we have such few SQL calls in the run-time.  We feel Ptah will *not* be a bottleneck for your application.  Ptah goes out of its way to do start-up time computation to minimize runtime overhead.

Ptah does not use Jinja, Mako, etc. Why?
----------------------------------------

We are still debating this.  It is possible to make Ptah not require Chameleon.  The goal is that developers can get an add-on and have it work seamlessly.  Having developers expect to use a single templating engine is reasonable; it reduces the amount of choices they need to make.  Also if they are interested in the add-on functonality they are probably committed to Ptah; so whatever template engine decision Ptah makes - the developer will be willing to accept that decision.

Chameleon is mature, fast, and feature rich.  The two most critized aspects of Chameleon are DOM attirbute markup and METAL.  Building composable applications (applications which use lots of addons) which require accessibility would be quite painful without attirbute markup.  METAL is Chameleon's template composition machinery; it is advanced and confusing.  That is why Ptah's view machinery provides a layout concept so programmers do not have to use METAL (unless they choose) and we feel it makes template composition more explicit and more easily understood.

Ptah uses zope.interface and adapters
-------------------------------------

It is true the internal implementation uses zope.interface and adapters. Ptah's public API *does not* require using any interfaces.  It is recommended against using adapter or zope.interface unless you are a framework developer.  It is worthwhile to note that Pyramid uses zope.interface to great success and hides its usage from the client programmer.  You will never had to use zope.interface in Ptah unless you *choose* to use them.

Ptah Manage isnt as Powerful as Django Admin
--------------------------------------------

The Ptah Manage facility is not meant to be a extension point for end users.  It is meant for developers and/or systems administrators to use.  Ptah App is what we assume would be useful for end users to interact with and that is why it exists.  You may see similarities between the two "Admin" systems but really the only aspect which is comparable is the SQLAlchemy introspection mechanism in Ptah Manage.  Which is really meant for quick and dirty review/edits of raw data.   Remember manipulating data through SQLAlchemy module in Ptah Manage does *not* notify the application of the event; so subscribers in the application will not be able to react to such data changes.

SQLAlchemy is Complex and Scary
-------------------------------

SQLAlchemy is a comprehensive library and an effect of that is it can feel overwhelming when reviewing the documentation.  You do not need to understand SQLAlchemy deeply is use Ptah.  The models that you write will most likely be simple and you will need to add behavior to them.  We believe 99% of developers will never have to learn anything "deep".

SQLAlchemy also has books written on it and is ported to Python 3.  There is a large friendly user community that is willing to answer questions.  It is a solid foundation to build on top.

See content.rst for example of SQLAlchemy usage.  

Why do you say REST and Websockets are First Class?
---------------------------------------------------

If your content model inherients from ptah_cms.Content than it will automatically be exposed via the Ptah REST API.  You will be able to update and call REST Actions on your models over REST.  We say its first class because the framework treat REST as important as it does its SQL data model.

Websocket integration is a bit trickier at the moment.  We are still feeling our way around how this will work.  We want developers to be able to use websocket's with their models in the context of the security system without having to think too much.  There will be a better answer soon.

Ptah doesnt work in my browser
------------------------------

As of this writing we have not started pushing the boundaries of HTML5.  We expect release of Ptah to not work in browsers without HTML5 support.  Ptah is aiming for web browsers IE9/10 and latest Firefox, Chrome and Safari as of end of 2011.  If your browser does not work - you can read the documentation and customize the templates to work with your or your customers browsers.

Backwards compatibility (especially regarding browsers) is a non-priority for Ptah.  We are aiming to support current and future browser standards not standards we have had foisted upon us as of today. 

Ptah cheats and uses SQL like NoSQL
-----------------------------------

The core ptah_cms data model is very simple and meant to be extensible.
We do store JSON for some attributes (like security) instead of separate tables for performance and convienance reasons.  Ptah isnt a academic
exercise it is to help people get work done efficiently.  The core data
model is simple enough that you can normalize your schema's however you
like but that doesnt mean the core system needs to have that complexity.
The other "cheat" is that we store path in the content table.  This enables
fast lookups if using content heirarchies (1 simple SELECT).  ptah_cms
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

You do not need to use traversal/containment with Ptah.  You can still use nearly all of ptah_cms.  Containment is useful concept and it is how many users think about website management.  After all Apache uses containment; just instead of a database it uses a filesystem.

I hate Pyramid, why would I use Ptah?
-------------------------------------

If you dislike Pyramid's design than most likely you will not like Ptah.
Ptah takes a lot of design cues from Pyramid.  We believe Pyramid is a great balance of design and practicality.  Since Pyramid is low level it does require you to write your own login form, etc.  But that is where Ptah comes in.  Hopefully Ptah will give you more insight into how fun Pyramid really is.

