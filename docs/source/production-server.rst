.. _production-setup:

Production Setup with Gunicorn, Nginx, and Supervisor
=====================================================

Production setup of the Kegbot server consists of the following components:

* `Nginx <http://nginx.org/>`_ (public facing web server)
* `Gunicorn <http://gunicorn.org/>`_ (internal HTTP application server)
* `supervisord <http://supervisord.org/>`_ (process control and monitor)

This chapter will guide you though running these two components.

.. note::
  It is possible to use other components in place of the ones recommended here;
  you'll need to figure out those steps yourself.

Gunicorn
--------

Starting with version 0.9.4, Gunicorn is automatically installed with Kegbot
Server.  You can test it with the built-in command, ``run_gunicorn``::
  
  (kb) $ kegbot-admin.py run_gunicorn --debug

If this works, you're ready to fire up nginx.

Nginx
-----

Install Nginx
~~~~~~~~~~~~~

Nginx is a fast and flexible HTTP server written in C. You can install it with
the ``nginx`` package on Ubuntu::
  
  $ sudo apt-get install nginx

After nginx is installed and started, a default HTTP server will be running on
port 80.

Create Kegbot nginx config
~~~~~~~~~~~~~~~~~~~~~~~~~~

Kegbot includes a sample nginx configuration file in the ``deploy/`` directory
which needs to be tailored to your setup.  The contents are also included below:

.. include:: ../../deploy/kegbot-nginx.conf
  :code:

Create a copy of this file, editing the paths noted in the comments at the top.
Finally, install it::
  
  $ sudo cp kegbot-nginx.conf /etc/nginx/sites-available/
  $ sudo rm /etc/nginx/sites-enabled/default
  $ sudo ln -s /etc/nginx/sites-available/kegbot-nginx.conf /etc/nginx/sites-enabled/
  $ sudo service nginx restart

supervisord
-----------

Install supervisor using ``apt-get``::
  
  $ sudo apt-get install supervisor

Supervisor manages programs according to its configuration files. Once again,
there is a template in the ``deploy/`` directory:

.. include:: ../../deploy/kegbot-supervisor.conf
  :code:

Make a copy of this file, editing the fields as noted, and install it::
  
  $ sudo cp kegbot-supervisor.conf /etc/supervisor/conf.d/kegbot.conf

Restart supervisor so that it reads the Kegbot config::
  
  $ sudo service supervisor restart

Finally, launch the web server (and celery, if installed)::
  
  $ sudo supervisorctl start kegbot:gunicorn
  $ sudo supervisorctl start kegbot:celery   # optional

