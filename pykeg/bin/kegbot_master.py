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

"""Master Kegbot process runner.

This program simplifies running multiple Kegbot processes as daemons.
"""

import importhacks

import ConfigParser
import commands
import os
import signal
import sys
import time

from pykeg.core import kb_app
from pykeg.core import util

from pykeg.external.gflags import gflags

FLAGS = gflags.FLAGS

gflags.DEFINE_string('master_config', '/etc/kegbot/master.cfg',
    'Path to the master config file.')

STATUS_UNKNOWN = -1
STATUS_ALIVE = 1
STATUS_DEAD = 2
STATUS_STOPPED = 3

class KegbotMasterApp(kb_app.App):
  def _Setup(self):
    kb_app.App._Setup(self)
    self._config = ConfigParser.ConfigParser()
    self._config.read(FLAGS.master_config)
    self._commands = {}

    for app in self._EnabledApps():
      self._commands[app] = self._BuildCommand(app)

  def _Enabled(self, app):
    return self._config.getboolean(app, '_enabled')

  def _AllAppNames(self):
    return self._config.sections()

  def _EnabledApps(self):
    apps = self._AllAppNames()
    return (app for app in apps if self._Enabled(app))

  def _BuildCommand(self, app):
    cmd = [self._config.get(app, '_program_name')]
    flags = []

    options = self._config.items(app)
    for flag, value in options:
      if flag.startswith('_'):
        continue
      if value:
        flags.append('--%s=%s' % (flag, value))
      else:
        flags.append('--%s' % (flag,))

    flags.sort()
    ret = cmd + flags
    return ret

  def _PrettyCommand(self, cmdlist):
    options = ''
    command = cmdlist[0]
    if len(cmdlist) > 1:
      options = ' \\\n'.join('    %s' % cmd for cmd in cmdlist[1:])
      return '%s \\\n%s' % (command, options)
    else:
      return command

  def _Usage(self):
    sys.stderr.write('Usage: %s <start|stop|status|configtest>\n' %
        self._extra_argv[0])

  def _StartApps(self):
    self._logger.info('Starting apps')
    for app in self._AllAppNames():
      if app not in self._commands:
        continue
      command = self._commands[app]
      command_str = ' '.join(command)
      self._logger.info('Starting: %s' % app)
      self._logger.info('Command: %s' % command_str)
      status, output = commands.getstatusoutput(command_str)
      if status == 0:
        self._logger.info('Started %s OK' % app)
      else:
        self._logger.error('Error starting %s: %i' % (app, status))
        output_lines = output.splitlines()
        if len(output_lines):
          self._logger.error('Output was:')
          for line in output_lines:
            self._logger.error('<%s>  %s' % (app, line))
        break

  def _AppStatus(self, app):
    pidfile = self._config.get(app, 'pidfile')
    if not os.path.exists(pidfile):
      return STATUS_STOPPED, -1
    try:
      pid_fd = open(pidfile, 'r')
      pid = int(pid_fd.readline().strip())
      alive = util.PidIsAlive(pid)
      if alive:
        return STATUS_ALIVE, pid
      else:
        return STATUS_DEAD, pid
    except (IOError):
      pass
    return STATUS_UNKNOWN, -1

  def _Status(self):
    stats = {}
    for app in self._AllAppNames():
      if app not in self._commands:
        continue
      status, pid = self._AppStatus(app)
      if status == STATUS_ALIVE:
        stats[app] = 'running (%i)' % (pid,)
      elif status == STATUS_DEAD:
        stats[app] = 'died (%i)' % (pid,)
      elif status == STATUS_STOPPED:
        stats[app] = 'stopped'
      else:
        stats[app] = 'unknown'

    print 'Status:'
    for app, status in stats.iteritems():
      print '%24s : %s' % (app, status)

  def _ConfigTest(self):
    print '# These are the commands that would be executed on start:'
    print ''

    for app in self._EnabledApps():
      print '# %s' % app
      print self._PrettyCommand(self._commands[app])
      print ''

  def _StopApps(self):
    for app in self._EnabledApps():
      attempts = 0
      signum = signal.SIGTERM
      self._logger.info('Stopping app: %s' % app)
      while True:
        status, pid = self._AppStatus(app)
        if status != STATUS_ALIVE:
          self._logger.info('%s stopped.' % app)
          break
        self._logger.info('Sending app %s signal %i' % (app, signum))
        os.kill(pid, signum)
        time.sleep(1.0)
        attempts += 1
        if attempts == 3:
          signum = signal.SIGKILL
        if attempts >= 6:
          self._logger.error('Too many attempts, aborting')
          break

  def _MainLoop(self):
    if len(self._extra_argv) != 2:
      self._Usage()
      sys.exit(1)
    command = self._extra_argv[1]

    if command == 'start':
      self._StartApps()
    elif command == 'stop':
      self._StopApps()
    elif command == 'status':
      self._Status()
    elif command == 'configtest':
      self._ConfigTest()
    else:
      self._Usage()
      sys.exit(1)


if __name__ == '__main__':
  KegbotMasterApp.BuildAndRun(name='master')
