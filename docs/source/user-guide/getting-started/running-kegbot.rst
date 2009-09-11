.. _running-kegbot:

Running Kegbot
==============

Congratulations! You're now ready to start up Kegbot.  There are a few programs
included in the ``bin/`` directory of ``pykeg`` that you will now become
familiar with::
* ``kegbot_admin.py``, an administrative utility tool
* ``kegbot_core.py``, the core kegbot daemon
* ``kegboard_daemon.py``, the daemon that listens to the kegboard

Install Databases
-----------------

There's actually one last step before you can begin: you must install the kegbot
tables into the new database::

	% cd $KEGBOT_HOME/pykeg
	% make setup
	--- Installing database
	Syncing...
	Creating table auth_permission
	Creating table auth_group
	Creating table auth_user
	Creating table auth_message
	Creating table django_content_type
	Creating table django_session
	Creating table django_site
	Creating table django_admin_log
	Creating table core_userpicture
	Creating table core_userlabel
	Creating table core_userprofile
	Creating table core_brewer
	Creating table core_beerstyle
	Creating table core_beertype
	Creating table core_kegsize
	Creating table core_kegtap
	Creating table core_keg
	Creating table core_drink
	Creating table core_token
	Creating table core_bac
	Creating table core_userdrinkingsession
	Creating table core_userdrinkingsessionassignment
	Creating table core_drinkingsessiongroup
	Creating table core_thermolog
	Creating table core_relaylog
	Creating table core_config
	Creating table twitter_usertwitterlink
	Creating table twitter_tweetlog
	Creating table twitter_drinktweetlog
	Creating table twitter_drinkclassification
	Creating table twitter_drinkremark
	Creating table kegweb_page
	Creating table accounting_billstatement
	Creating table accounting_drinkcharge
	Creating table accounting_misccharge
	Creating table accounting_payment
	Creating table registration_registrationprofile
	Creating table south_migrationhistory
	Installing index for auth.Permission model
	Installing index for auth.Message model
	Installing index for admin.LogEntry model
	Installing index for core.BeerType model
	Installing index for core.KegTap model
	Installing index for core.Keg model
	Installing index for core.Drink model
	Installing index for core.Token model
	Installing index for core.BAC model
	Installing index for core.UserDrinkingSession model
	Installing index for core.UserDrinkingSessionAssignment model
	Installing index for twitter.DrinkTweetLog model
	Installing index for twitter.DrinkRemark model
	Installing index for kegweb.Page model
	Installing index for accounting.BillStatement model
	Installing index for accounting.DrinkCharge model
	Installing index for accounting.MiscCharge model
	Installing index for accounting.Payment model
	
	Synced:
	 > django.contrib.auth
	 > django.contrib.contenttypes
	 > django.contrib.sessions
	 > django.contrib.sites
	 > django.contrib.admin
	 > django.contrib.markup
	 > pykeg.core
	 > pykeg.contrib.twitter
	 > kegweb.kegweb
	 > kegweb.accounting
	 > registration
	 > south
	
	Not synced (use migrations):
	 - 
	(use ./manage.py migrate to migrate these)
	Running migrations for core:
	 - Migrating forwards to 0002_delete_keg_channel.
	 > core: 0001_initial
		 (faked)
	 > core: 0002_delete_keg_channel
		 (faked)
	Running migrations for twitter:
	 - Migrating forwards to 0001_initial.
	 > twitter: 0001_initial
		 (faked)
	Running migrations for kegweb:
	 - Migrating forwards to 0001_initial.
	 > kegweb: 0001_initial
		 (faked)
	Running migrations for accounting:
	 - Migrating forwards to 0001_initial.
	 > accounting: 0001_initial
		 (faked)
	Setting database defaults.
	--- Creating super user
	Username (Leave blank to use 'mike'): 
	E-mail address: mike@example.com
	Password: 
	Password (again): 
	Superuser created successfully.


Run Kegbot Core
---------------

You're now ready to run the Kegbot core process!::

	% ./bin/kegbot_core.py
	2009-09-10 00:23:36,259 INFO     (tap-manager) Registering new tap: flow0
	2009-09-10 00:23:36,466 INFO     (main) Starting all service threads.
	2009-09-10 00:23:36,466 INFO     (main) starting thread "alarmmanager-thread"
	2009-09-10 00:23:36,474 INFO     (main) starting thread "eventhub-thread"
	2009-09-10 00:23:36,475 INFO     (main) starting thread "net-thread"
	2009-09-10 00:23:36,476 INFO     (net-thread) network thread started
	2009-09-10 00:23:36,476 INFO     (main) starting thread "flowmonitor-thread"
	2009-09-10 00:23:36,477 INFO     (main) starting thread "service-thread"
	2009-09-10 00:23:36,478 INFO     (main) starting thread "watchdog-thread"
	2009-09-10 00:23:36,479 INFO     (main) All threads started.

If successful, you should see something like the above.

You can also see options for any application in ``bin/`` by using the ``--help``
or ``--helpshort`` flags::
	% ./bin/kegbot_core.py --help
	Kegbot Core Application.
	
	This is the Kegbot Core application, which runs the main drink recording and
	post-processing loop. There is exactly one instance of a kegbot core per kegbot
	system.
	
	For more information, please see the kegbot documentation.
	
	flags:
	
	pykeg.core.kb_app:
		--[no]daemon: Run application in daemon mode
			(default: 'false')
		-?,--[no]help: show this help
		--[no]helpshort: show usage only for this module
		--[no]log_to_file: Send log messages to the log file defined by --logfile
			(default: 'true')
		--[no]log_to_stdout: Send log messages to the console
			(default: 'true')
		--logfile: Default log file for log messages
			(default: 'kegbot.log')
		--logformat: Default format to use for log messages.
			(default: '%(asctime)s %(levelname)-8s (%(name)s) %(message)s')
		--[no]verbose: Generate extra logging information.
			(default: 'false')
	
	pykeg.core.net.kegnet_server:
		--kb_core_bind_addr: Address that the kegnet server should bind to.
			(default: 'localhost:9805')
	
	google3.pyglib.flags:
		--flagfile: Insert flag definitions from the given file into the command line.
			(default: '')
		--undefok: comma-separated list of flag names that it is okay to specify on
			the command line even if the program does not define a flag with that name.
			IMPORTANT: flags in this list that have arguments MUST use the --flag=value
			format.
			(default: '')

