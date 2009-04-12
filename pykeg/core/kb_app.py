#!/usr/bin/env python
#
# Copyright 2009 Mike Wakerly <opensource@hoho.com>
#
# This file is part of the Pykeg package of the Kegbot project.
# For more information on Pykeg or Kegbot, see http://kegbot.org/
#
# Pykeg is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Pykeg is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pykeg.  If not, see <http://www.gnu.org/licenses/>.

"""Kegbot Application module.

Module for common logic for a command line or daemon application.
"""

import logging
import signal
import sys

from pykeg.core import util
from pykeg.external.gflags import gflags

FLAGS = gflags.FLAGS

gflags.DEFINE_boolean('daemon', False,
    'Run application in daemon mode')

gflags.DEFINE_string('logformat',
    '%(asctime)s %(levelname)-8s (%(name)s) %(message)s',
    'Default format to use for log messages.')

gflags.DEFINE_string('logfile',
    'kegbot.log',
    'Default log file for log messages')

gflags.DEFINE_boolean('log_to_file', True,
    'Send log messages to the log file defined by --logfile')

gflags.DEFINE_boolean('log_to_stdout', True,
    'Send log messages to the console')


class App(object):
  """Application instance container.

  Scripts and daemons wishing to reuse the application logic here should
  subclass App, and implement some or all of _Setup and _MainLoop.
  """

  def __init__(self, name='main', daemon=False):
    self._name = name
    self._is_daemon = daemon
    self._do_quit = False
    self._threads = set()

    try:
      argv = FLAGS(sys.argv)  # parse flags
    except gflags.FlagsError, e:
      print 'Usage: %s ARGS\n%s\n\nError: %s' % (sys.argv[0], FLAGS, e)
      sys.exit(1)

    self._SetupLogging()
    self._SetupSignalHandlers()
    self._logger = logging.getLogger(self._name)

  @classmethod
  def BuildAndRun(cls, name='main', daemon=False):
    """Convenience class method to create and Start the app."""
    if sys.version_info < (2,4):
      print>>sys.stderr, 'kegbot requires Python 2.4 or later; aborting'
      sys.exit(1)

    app = cls(name, daemon)
    app.Start()

  def Start(self):
    """Perform setup and run the application main loop."""
    self._Setup()
    self._StartThreads()
    self._MainLoop()

  def _Setup(self):
    """Perform app-specific setup.

    This function is called by Start. Subclasses should call the superclass
    _Setup method (or provide similar functionality.
    """
    if self._is_daemon:
      self._logger.info('Daemon mode requested, switching to background.')
      util.daemonize()
      self._logger.info('Running in background.')

  def _StartThreads(self):
    """Start any threading.Thread objects registered in _threads."""
    if not len(self._threads):
      return
    self._logger.info('Starting all service threads.')
    for thr in self._threads:
      self._logger.info('starting thread "%s"' % thr.getName())
      thr.start()
    self._logger.info('All threads started.')

  def _StopThreads(self):
    """Stop any threading.Thread objects registered in _threads."""
    if not len(self._threads):
      return
    self._logger.info('Stopping all service threads.')
    for thr in self._threads:
      if thr.isAlive():
        self._logger.info('stopping thread "%s"' % thr.getName())
        thr.Quit()
      if thr.isAlive():
        thr.join(2.0)
    self._logger.info('All service threads stopped.')

  def _MainLoop(self):
    """Run the (possibly app-specific) main loop."""
    self._logger.info('Running generic main loop (going to sleep).')
    while True:
      time.sleep(1000)

  def _DumpStatus(self):
    self._logger.info('-------- Begin Status Dump --------')
    if len(self._threads):
      self._logger.info('Status of threads:')
    for thr in self._threads:
      if thr.isAlive():
        thrstatus = 'running'
      else:
        thrstatus = '   DEAD'
      self._logger.info('  %s:  %s' % (thrstatus, thr.getName()))
    self._logger.info('-------- End Status Dump --------')

  def _AddAppThread(self, thr):
    """Add a threading.Thread to the set of registered threads.

    Threads added this way will be owned by the app, and automatically started
    and stopped with the main application.
    """
    self._threads.add(thr)

  def Quit(self):
    """Run the (possibly app-specific) Quit routines."""
    self._do_quit = True
    self._StopThreads()
    self._TeardownLogging()

  def _SetupLogging(self, level=logging.INFO):
    logging.root.setLevel(level)

    # add a file-output handler
    self._logging_file_handler = None
    if FLAGS.log_to_file:
      self._logging_file_handler = logging.FileHandler(FLAGS.logfile)
      formatter = logging.Formatter(FLAGS.logformat)
      self._logging_file_handler.setFormatter(formatter)
      logging.root.addHandler(self._logging_file_handler)

    # add tty handler
    self._logging_stdout_handler = None
    if FLAGS.log_to_stdout and not self._is_daemon:
      self._logging_stdout_handler = logging.StreamHandler(sys.stdout)
      formatter = logging.Formatter(FLAGS.logformat)
      self._logging_stdout_handler.setFormatter(formatter)
      logging.root.addHandler(self._logging_stdout_handler)

  def _TeardownLogging(self):
    if self._logging_file_handler:
      logging.root.removeHandler(self._logging_file_handler)
      self._logging_file_handler = None
    if self._logging_stdout_handler:
      logging.root.removeHandler(self._logging_stdout_handler)
      self._logging_stdout_handler = None

  def _SetupSignalHandlers(self):
    """Set up handlers for signals received by main process.

    Sets HUP, INT, QUIT, TERM to cause a quit;
    Sets USR1 to cause a status dump.
    """
    signal.signal(signal.SIGHUP, self._QuitSignalHandler)
    signal.signal(signal.SIGINT, self._QuitSignalHandler)
    signal.signal(signal.SIGQUIT, self._QuitSignalHandler)
    signal.signal(signal.SIGTERM, self._QuitSignalHandler)
    signal.signal(signal.SIGUSR1, self._DumpSignalHandler)

  def _QuitSignalHandler(self, signum, frame):
    """ All handled signals cause a quit """
    self._logger.info('Got signal %i' % signum)
    self.Quit()

  def _DumpSignalHandler(self, signum, frame):
    self._DumpStatus()
