What Makes Ptah Unique
======================

Pyramid
-------

Since Ptah is built on top of Pyramid you should familiarize yourself
with what makes `Pyramid Unique <https://docs.pylonsproject.org/projects/pyramid/1.2/narr/introduction.html#what-makes-pyramid-unique>_`
    
Ptah is trying to keep with the Pyramid motif, "Eat what you pay for".
Although a CMS does need to have an opinion, which we have in spades. 
Ptah shares many of the values and design decisions of Pyramid.  Runtime
flexibility of every possible aspect of the CMS is a waste of resources.
We want to compute as much as possible at startup time and carefully outline
WHAT limitations we will impose on runtime configuration.  For instance you 
can not add ad-hoc Permissions at runtime.  You add a Permission and restart 
the server.  After all if you are adding Permissions at runtime - there is
certainly a better way.  

Eat What You Pay For
--------------------

CMS and Application frameworks are not known for their "eat what you pay for".  
We have designed the system so you can use most of the Ptah core features without 
having to use "the entire web ui, CMS and associated features".  

Performance
-----------

Since Ptah uses a RDBMS (via SqlAlchemY) Ptah is much much slower than your 
traditional "hello world" benchmarks.  While Pyramid may get 3000+ req/second 
serving a response, there simply is no comparable benchmark for web 
applications/content frameworks.  We aim to stay between 110-130 request/second
(per single threaded python process). Today on 2010 macbook pro we get 230-240
requests/second.  Remember we are applying security and doing heavily lifting.
Python, on a whole, is reasonably fast.  Pypy should make us go between 
1.5x and 3x faster.

Evolution not Revolution
------------------------

You can plug-in Ptah into your web application after it has been
deployed.  You should not have to alter your web application to
stitch in Ptah.  For instance, you have a web application which
has already been built (you have a lot of routes, for example) - you
can decide where you want the CMS to participate.

Data model
----------

Ptah specifies a relational data model which varies with degrees of
features (ptah is simpler than ptah_cms which, in turn, is simpler
that ptah_app).  We chose a dirt-simple relational data model that
emphasizes pragmatism over purity.  It should be approachable by
anyone who has previous database experience. 

  - ptah_cms_nodes

  - ptah_cms_content

Security
--------
The most difficult aspect of complex web frameworks is consistenty enforcing
authorization policies.  This is a critical aspect when there is a large 
aftermarket of add-ons and a vibrant community of developers contributing 
and re-using software.   
    
A security story::
      
      Bob Dobbs creates a Poll component which has a number of features
      you would like to re-use.  You install it and configure it to
      show up in /polls.  To view a poll you GET /polls/$id and to
      vote you POST /polls/$id.  The only integration with Ptah is that
      he wanted it to be accessible through the auto-generated REST API.
      So Polls have a entry in ptah_cms_nodes (for its URI feature).
      
      After you have used the Poll for some time you find yourself with
      the requirement, "Some Polls need to be displayed on a particular
      page in your website, unfortunately, the section on the website
      has security restrictions preventing only "Internal Staff" or a similar
      role to see content in this section.  You have never needed security
      on any Polls.  Fortunately since this Poll add-on participates with
      the ptah_cms_nodes table, you can simply set the `parent` attribute
      (which would have been null on Polls until this date) to the Page
      where you will be showing the Poll. 
      
      After doing that anyone who attempts to goto /polls/$secure_pollid
      but they do not have the correct roles will get a Forbidden error.
      Also the REST api for that poll will also be protected without any
      future work from you.

Flat is Better than Nested
--------------------------
While you can treat the content in the Ptah CMS as "heirarchical", in reality,
it is flat.  We have 2 attributes we use for mapping on to heirarchies: 
ptah_cms_nodes.parent_uri and the ptah_cms_content.path columns.  The path
attribute is how we efficiently do fast look ups.  Walking parent/children 
relationships in a RDBMS is inefficient, say, compared to graph databases such
as ZODB or Neo4J. RDBMS arent graphs.  The REST API is another example of this
mantra.

REST as First Class Citizen
---------------------------

By participating in the basic ptah_cms.content datamodel; your content can be 
READ/UPDATED/DELETED via a REST URL without any work from you.  And security
will be applied to your models.  Install Ptah and curl
http://localhost:8080/__rest__/cms/ - we believe you wont be disappointed.

URIs Everywhere
---------------

A core feature of this system is data sources will be integrated gratitiously.
One thing that Plone has taught us is that if there is a service/persistence 
engine; people will want to integrate into it (and expect it to participate 
in all of the CMS services).  URI are the token which represents a record, 
be that a user record or a content record.  
    
Other storages
--------------

Aim to support ZODB, Mongo and other NoSQL databases integrations in a natural 
way.  We have a lot of experience with ZODB, BerkelyDB and other "No SQL" 
systems.  We believe we can provide a cohesive way to mix such "No SQL" records
into the CMS system.  What does that mean?  That records in those external 
systems can have security applied if they are being loaded through Ptah.  
Security, workflow, and other services Ptah provides.  Ptah will never have a
`pluggable` storage engine.  

Easy to Fork
------------

A goal to keep the software small is to encourage people to fork Ptah and
use it with different storages.  Until we are convinced otherwise the Ptah
project will use a relational database.  Please fork Ptah and replace
RDBMS with Mongo or some other persistence system and tell us.

Readability
-----------

When there is a decision to be made between legiblity of source code and
performance we will opt for the readibility avenue.  Follow pep8 guidelines and
consistent naming.

Future Proof
------------

Ptah aims to be the first comprehensive CMS framework which will work with
Python 3.  All work done on Ptah around User Interface and User Experience
will use HTML5, CSS3, websockets and ARIA.  While many browsers do not 
fully support this at the end of 2011.  Browsers will in the next 12 months.
We hope to release a stable version around the time these browser features 
are widely available.  

Interactivity
-------------
The default ptah_app UI will require websockets for interactivity.
Ptah will still work by running simply 1 server (HTTP) but it will be 
recommended to run a second server dedicated to websockets.  We aim to provide
facilities which will make developing security interactive web applications
pleasant.

Exclusion over Inclusion
------------------------
We know this is controversial and possible anti-Pyramid but hear us out.
Pyramid requires the developer to be explicit and you specifically say you
want to load a package.  Ptah *does not* do this.  If you have a package
in your PYTHONPATH that has a entry-point for `memphis`; it will get loaded.
This is the default behavior and, of course, you can manually Configure your
usage of Ptah the same way you configure Pyramid.  

But why?  Because the goal of Ptah is to support a class of developer who
wants to casually experiment with the system.  They should be able to install
a egg and restart service and have it work.  We do understand that this goes
against the Pyramid culture - so we will strive to document and support the
Pyramid way.