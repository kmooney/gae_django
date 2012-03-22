.. GAE Django 

Building Scalable Web Applications with Appengine
=================================================

by Robert Myers

robert@keyingredient.com

Topics
------

* About Google Appengine
* Whats new in latest version
* Django on Appengine
* Appengine Models vs Django Models
* Other wsgi frameworks
* Building a pinterest clone
* How to scale your internet sensation
* Advanced tools

What's in it for me?
====================

Why should I use Google Appengine?
----------------------------------

* PAAS vs IAAS
* Security
* Auto Scaling
* MegaStore (big table)
* TaskQueue
* Blobstore
* ProtoRPC
* memcache

Whats new in the latest SDK
===========================

New Features
------------

* Python 2.7
* Multithreading
* Django 1.3
* NumPy
* lxml
* less runtime restrictions

Django on Appengine
===================

Cause its fun!!
---------------

.. image:: _static/django.png

Tips
----

* Don't use django-nonrel
* Learn to love the datastore
* Shameless plug: use gae_django

``gae_django`` 
===============

http://github.com/rmyers/gae_django/

Features
--------

* AdminSite that works with Appengine
* Auth backends (oauth support)
* Transaction support
* http://github.com/rmyers/gae_django

Datastore vs Django ORM
============================

Differences
-----------

===============  ==============
Datastore        Django ORM 
===============  ==============
Proprietary      Open Source 
NoSQL            SQL
Entity Groups    Relations
Auto Scaling     Manual Scaling
Index Required   Ad-hoc Queries
===============  ==============

Similarities
------------

Datastore::

    from google.appengine.ext import db
    class MyModel(db.Model):
        field_one = db.StringProperty(indexed=False)
        field_two = db.EmailProperty(required=True)
    
    obj = MyModel.all().filter('field_two =', 'jim@jones.com').get()

Django::

    from django.db import models
    class MyModel(models.Model):
        field_one = models.CharField(dbindex=False)
        field_two = models.EmailField(required=True)
    
    obj = MyModel.objects.filter(field_two='jim@jones.com').get()

Entity Groups
-------------

* Groups Models in a Hierarchy::

    Parent > child one
           > child two > grandchild one
           > child three > grandchild two

* Stored together on same server.
* Fast and easy to get related entities::

    >>> print grandchild.all().ancestor(parent).fetch(10)
    [<grandchild one>, <grandchild two>]

* Be careful about adding too much as the entire group is locked during
  a transaction.

Datastore Keys
--------------

Look like random hashstrings::

    >>> str(MyEntity.key())
    'ahBzfm1hbnRlcmVzdC1wcm9kcgsLEgRVc2VyGPEuDA'
    
But are secretly datastructures::

    >>> key = 'ahBzfm1hbnRlcmVzdC1wcm9kcgsLEgRVc2VyGPEuDA'
    >>> mod = len(key) % 4
    >>> key += ('=' * (4 - mod))
    >>> key
    'ahBzfm1hbnRlcmVzdC1wcm9kcgsLEgRVc2VyGPEuDA=='
    
Anyone guess what this is?

Keys Continued
--------------

Hidden Values::

    >>> from base64 import urlsafe_b64decode
    >>> from google.appenine.datastore import entity_pb
    >>> obj = entity_pb.Reference(urlsafe_b64decode(key))
    >>> print obj
    app: "s~manterest-prod"
    path <
      Element {
        type: "User"
        id: 6001
      }
    >

So how do we use keys?
----------------------

You can easily construct unique keys and use that to insert into the datastore::

    key = db.Key().from_path('MyModel', 'arbitrary_key_name')
    m = MyModel(key=key, field_one='blah', field_two='bob@email.com')
    m.put()

Later we can do the reverse (efficiently)::

    key = db.Key().from_path('MyModel', 'arbitrary_key_name')
    m = db.get(key)

Efficient multi-get
-------------------
    
Or grab multiple unrelated objects at the same time::

    key1 = db.Key().from_path('MyModel', 'arbitrary_key_name')
    key2 = db.Key().from_path('OtherModel', 3422) # id
    key3 = db.Key().from_path('StillOtherModel', 36) # id
    m1, m2, m3 = db.get([key1, key2, key3])

Other wsgi frameworks
=====================

webapp2
-------

* Default wsgi app with python2.7
* Simple lightweight REST style class views
* Jinja or Django Templates 

Sample
------

WSGI Setup::

    import webapp2

    urls = [
        (r'/', 'views.IndexHandler'),
        webapp2.Route(r'^/user/<user_id:\d+>', 'views.UserHandler'),
    ]
    
    config = {}
    config['webapp2_extras.sessions'] = {
        'secret_key': 'something-very-very-secret',
    }

    app = webapp2.WSGIApplication(routes=urls, debug=True, config=config)

webapp2 Request
---------------

``views.py``::
    
    class IndexHandler(webapp2.RequestHandler):
        def get():
            self.response.write('Hello world')
    
    class UserHandler(webapp2.RequestHandler):
        def get(self, user_id):
            user = User.get_by_id(user_id)
            self.response.write(unicode(user))
        def post(self, user_id):
            form = MyForm(self.request.POST)
            if form.is_valid():
                # update User
                user.put()
            return self.redirect('/')

Building a pinterest clone
==========================

Let's call it Manterest, *"The Manliest place on the Internet"*

Manterest
---------

A place for Men to collect pictures and links to stuff for men.

* A model to store pictures/link/title
* A gallery view of resent 'mans' 
* Comments on 'mans'
* Follow feature for favorite users

How to scale your internet sensation?
=====================================

Advanced tools
==============

    
.. toctree::
   :maxdepth: 2