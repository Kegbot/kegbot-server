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

"""Simple event-passing mechanisms.

This module implements a very simple inter-process event passing system
(EventHub), and corresponding message class (Event).
"""

import logging
import Queue

class EventHub(object):
  """Central sink and publish of events."""
  def __init__(self):
    self._event_listeners = set()
    self._event_queue = Queue.Queue()
    self._logger = logging.getLogger('eventhub')

  def AddListener(self, listener):
    """Attach a listener, to be notified on receipt of a new event.

    The listener must implement the PostEvent(event) method.
    """
    if listener not in self._event_listeners:
      self._event_listeners.add(listener)

  def RemoveListener(self, listener):
    """Remove (by reference) an already-listening listener."""
    if listener in self._event_listeners:
      self._event_listeners.remove(listener)

  def PublishEvent(self, event):
    """Add a new event to the queue of events to publish.

    Events are dispatched to listeners in the DispatchNextEvent method.
    """
    self._event_queue.put(event)

  def _IterEventListeners(self):
    """Iterate through all listeners."""
    for listener in self._event_listeners:
      yield listener

  def _WaitForEvent(self, timeout=None):
    """Wait for a new event to be enqueued."""
    try:
      ev = self._event_queue.get(block=True, timeout=timeout)
    except Queue.Empty:
      ev = None
    return ev

  def DispatchNextEvent(self, timeout=None):
    """Wait for an event, and dispatch it to all listeners."""
    ev = self._WaitForEvent(timeout)
    if ev:
      self._logger.debug('Publishing event: %s %s' % (ev.DESCRIPTOR.name, ev))
      for listener in self._IterEventListeners():
        listener.PostEvent(ev)

