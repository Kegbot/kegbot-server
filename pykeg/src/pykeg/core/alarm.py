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

"""A general purpose timer/alarm manager."""

import heapq
import threading
import time

# TODO(mikey): add docstrings

class Alarm(object):
  def __init__(self, name, event, fire_time):
    self._name = name
    self._event = event
    self._fire_time = fire_time

  def __cmp__(self, other):
    return cmp(self.fire_time(), other.fire_time())

  def name(self):
    return self._name

  def fire_time(self):
    return self._fire_time

  def set_fire_time(self, fire_time):
    self._fire_time = fire_time

  def event(self):
    return self._event


class AlarmManager(object):
  def __init__(self):
    self._alarm_heap = []
    self._alarms_by_name = {}
    self._wake_event = threading.Event()
    self._wake_event.clear()
    self._heap_lock = threading.RLock()

  def _WakeEventWait(self, amt):
    self._wake_event.wait(amt)
    self._heap_lock.acquire()
    if self._wake_event.isSet():
      self._wake_event.clear()
    self._heap_lock.release()

  def WaitForNextAlarm(self, timeout=None):
    start = time.time()

    if timeout:
      wait_remain = timeout
      end = start + timeout
    else:
      wait_remain = None
      end = None

    while True:
      now = time.time()
      if timeout is not None:
        wait_remain = max(0, timeout - (now - start))

      # If there are no alarms, wait until we are notified
      self._heap_lock.acquire()

      if len(self._alarm_heap) == 0:
        self._heap_lock.release()
        if (timeout is None or wait_remain > 0):
          self._WakeEventWait(wait_remain)
          continue
        if (timeout is not None and wait_remain <= 0):
          # Ran out of time.
          return

      # Grab the next alarm.
      next_alarm = self._alarm_heap[0]
      now = time.time()

      # Now, we wait until the nearest alarm is due to fire. We can wake up
      # early if the wake_event gets set (which indicates the alarm list has
      # changed, meaning we should start over again).
      sleep_amt = max(0, next_alarm.fire_time() - now)

      # An alarm is ready now; remove it from the heap and process it.
      if sleep_amt == 0:
        popped = heapq.heappop(self._alarm_heap)
        self._heap_lock.release()
        assert(popped == next_alarm)
        return next_alarm

      self._heap_lock.release()

      # An alarm is not ready now; go to sleep and fetch it on the next
      # iteration of the loop.

      if timeout is not None:
        if wait_remain <= 0:
          return None
        wait_remain = max(0, timeout - (now - start))
        sleep_amt = min(sleep_amt, wait_remain)

      self._WakeEventWait(sleep_amt)

  def _DoAddAlarm(self, alarm):
    self._heap_lock.acquire()
    heapq.heappush(self._alarm_heap, alarm)
    self._alarms_by_name[alarm.name()] = alarm
    self._wake_event.set()
    self._heap_lock.release()

  def AddAlarm(self, name, expires_at, fire_event):
    """Add a new alarm that posts |fire_event| at |expires_at| time"""
    a = Alarm(name, fire_event, expires_at)
    self._DoAddAlarm(a)
    return a

  def CancelAlarm(self, name):
    self._heap_lock.acquire()
    match = None
    for alarm in self._alarm_heap:
      if alarm.name() == name:
        match = alarm
        break
    if match:
      del self._alarms_by_name[name]
      self._alarm_heap.remove(match)
      self._SortAlarms()
      self._wake_event.set()
    self._heap_lock.release()

  def UpdateAlarm(self, name, new_expires_at):
    """Replace an alarm's expiry with new time"""
    self._heap_lock.acquire()
    if name not in self._alarms_by_name:
      self._heap_lock.release()
      return
    alarm = self._alarms_by_name[name]
    alarm.set_fire_time(new_expires_at)
    self._SortAlarms()
    self._heap_lock.release()

  def _SortAlarms(self):
    self._heap_lock.acquire()
    heapq.heapify(self._alarm_heap)
    self._wake_event.set()
    self._heap_lock.release()

