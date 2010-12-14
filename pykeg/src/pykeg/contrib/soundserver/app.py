#!/usr/bin/env python
#
# Copyright 2010 Mike Wakerly <opensource@hoho.com>
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

"""SoundServer application implementation."""

import os
import ossaudiodev
import random
import Queue
import urllib2
import urlparse

import gflags
import mad

from pykeg.core import kb_app
from pykeg.core import units
from pykeg.core import util
from pykeg.core.net import kegnet
from pykeg.web.api import krest

FLAGS = gflags.FLAGS

gflags.DEFINE_string('cache_dir', '/tmp/sound_server_cache',
    'Directory for cached sound files.')

OUNCE_TRIGGER_THRESHOLDS = (32, 24, 16, 12, 8, 1, 0)

CREDIT_TRIGGER_THRESHOLDS = (100, 20, 10, 5, 1)


class SoundServerApp(kb_app.App):
  def __init__(self, name='sound_server'):
    kb_app.App.__init__(self, name)

  def _Setup(self):
    kb_app.App._Setup(self)

    sound_thread = SoundThread('sound-playback')
    self._AddAppThread(sound_thread)

    self._client = SoundClient(sound_thread)
    self._client.LoadEvents()
    self._client_thr = kegnet.KegnetClientThread('kegnet', self._client)
    self._AddAppThread(self._client_thr)


class SoundThread(util.KegbotThread):
  def __init__(self, name):
    util.KegbotThread.__init__(self, name)
    self._file_queue = Queue.Queue()
    self._logger.info('created sound thread')

  def Enqueue(self, filename):
    self._logger.info('Enqueue: %s' % filename)
    self._file_queue.put(filename)

  def ThreadMain(self):
    self._logger.info('in main loop')
    while not self._quit:
      try:
        filename = self._file_queue.get(timeout=0.5)
      except Queue.Empty:
        continue
      self._PlayFile(filename)

  def _PlayFile(self, filename):
    self._logger.info('Playing %s' % filename)
    mf = mad.MadFile(filename)
    dev = ossaudiodev.open('w')
    dev.speed(mf.samplerate())
    dev.setfmt(ossaudiodev.AFMT_S16_LE)
    dev.channels(2)
    while True:
      if self._file_queue.qsize():
        break
      buf = mf.read()
      if buf is None:
        break
      dev.write(buf)


class SoundClient(kegnet.SimpleKegnetClient):
  def __init__(self, sound_thread, addr=None):
    kegnet.SimpleKegnetClient.__init__(self, addr)
    self._sound_thread = sound_thread
    self._event_map = {}
    self._sound_file_map = {}
    self._tempdir = FLAGS.cache_dir
    self._flows = {}

  def PlaySoundFile(self, sound_url):
    local_sound = self._sound_file_map.get(sound_url)
    if not local_sound:
      self._logger.warning('No sound for "%s"' % sound_url)
      return

    self._sound_thread.Enqueue(local_sound)

  def PlaySoundEvent(self, event):
    soundfile = event.soundfile
    self.PlaySoundFile(soundfile)

  def LoadEvents(self):
    self._logger.info('Loading events')
    api_client = krest.KrestClient()
    all_events = api_client.AllSoundEvents()
    for event in all_events['events']:
      self.LoadSoundEvent(event)

  def LoadSoundEvent(self, event):
    self._CacheSound(event.sound_url)
    if event.event_name not in self._event_map:
      self._event_map[event.event_name] = list()
    self._event_map[event.event_name].append(event)

  def _CacheSound(self, sound_url):
    if sound_url in self._sound_file_map:
      return

    outfile = os.path.join(self._tempdir, os.path.basename(sound_url))
    self._sound_file_map[sound_url] = outfile

    if os.path.exists(outfile):
      self._logger.info('Cached file for "%s" exists at %s' % (sound_url, outfile))
      return

    dirname = os.path.dirname(outfile)
    if not os.path.exists(dirname):
      self._logger.info('Creating directory: %s' % dirname)
      os.makedirs(dirname)

    parts = urlparse.urlparse(sound_url)
    if not parts.scheme.startswith('http'):
      self._logger.error('URL for event does not start with http ("%s")' %
          sound_url)
      self._logger.error('Be sure MEDIA_URL in common_settings.py gives an '
                         ' absolute url.')
      return

    self._logger.info('Saving file "%s" to %s' % (sound_url, outfile))
    filedata = urllib2.urlopen(sound_url).read()
    outfd = open(outfile, 'wb')
    outfd.write(filedata)
    outfd.close()

  def onCreditAdded(self, event):
    amount = event.amount

    for threshold in CREDIT_TRIGGER_THRESHOLDS:
      if amount < threshold:
        continue
      events = self._GetMatchingEvents('credit.added.threshold', threshold)
      if len(events):
        soundevent = random.choice(events)
        self.PlaySoundFile(soundevent.soundfile)
        return

  def onFlowUpdate(self, event):
    flow_id = event.flow_id

    if event.state == event.FlowState.COMPLETED:
      if flow_id in self._flows:
        del self._flows[flow_id]
        return

    curr_ounces = float(units.Quantity(event.volume_ml,
        units=units.UNITS.Ounce, from_units=units.UNITS.Milliliter))

    if flow_id not in self._flows:
      self._flows[flow_id] = -1

    last_ounces = self._flows[flow_id]

    for trigger in OUNCE_TRIGGER_THRESHOLDS:
      if (last_ounces < trigger) and (curr_ounces >= trigger):
        self._ThresholdEvent(trigger, event)
        break
    self._flows[flow_id] = curr_ounces

  def _GetMatchingEvents(self, event_name, predicate=None, user=None):
    events = self._event_map.get(event_name, [])
    if predicate is not None:
      events = [e for e in events if e.event_predicate == str(predicate)]
    if user:
      events = [e for e in events if e.user == user]
    return events

  def _ThresholdEvent(self, trigger_ounces, flow_update):
    self._logger.info('Threshold [%i ounces] reached for flow %i' %
        (trigger_ounces, flow_update.flow_id))

    events = self._GetMatchingEvents('flow.threshold.ounces', trigger_ounces)
    self._logger.info('Events matching trigger: %s' % str(events))

    if len(events) == 0:
      return
    elif len(events) == 1:
      soundevent = events[0]
    else:
      soundevent = random.choice(events)

    self.PlaySoundFile(soundevent.sound_url)
