.. _running-kegbot:

Running Kegbot
==============

Congratulations! You're now ready to start up Kegbot.  There are a few programs
included in the ``bin/`` directory of ``pykeg`` that you will now become
familiar with:

* ``kegbot_admin.py``, an administrative utility tool
* ``kegbot_core.py``, the core kegbot daemon
* ``kegboard_daemon.py``, the daemon that listens to the kegboard

Run Kegbot Core
---------------

You're now ready to run the Kegbot core process::

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

Start up kegboard daemon
------------------------

TODO

Start up Kegweb
---------------

You can now start Kegweb. Try running the built in development server::

	% ./bin/kegbot_admin.py runserver 0.0.0.0:8000
	Validating models...
	0 errors found

	Django version 1.0.2 final, using settings 'pykeg.settings'
	Development server is running at http://0.0.0.0:8000/
	Quit the server with CONTROL-C.

Go to the kegweb URL in your browser, eg http://localhost/

Create a Keg
------------

TODO

