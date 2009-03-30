# Copyright 2008 Mike Wakerly <opensource@hoho.com>
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

import Queue
import types

from pykeg.core import util

class StateMachineDriver:
  def __init__(self, state_machine):
    self._event_queue = Queue.Queue()
    self._state_machine = state_machine

    self._state_insts = {}
    for cls in self._AllStateClasses():
      self._BuildState(cls)

    self._current_state = self._state_machine.InitialState
    self._DoTransition(StateMachine.EVENT.Unconditional, self._current_state,
                       self._current_state)

  def PushEvent(self, event):
    self._event_queue.put(event)

  def CurrentState(self):
    return self.StateInstance(self.CurrentStateCls())

  def CurrentStateCls(self):
    return self._current_state

  def _AllStateClasses(self):
    """ Return a set of all class pointers """
    ret = set()
    for orig_state, event_dict in self._state_machine.IterVerticies():
      ret.add(orig_state)
      for dest_state in event_dict.values():
        ret.add(dest_state)
    return ret

  def _BuildState(self, state_cls):
    """ Build the state instance for a particular state """
    assert type(state_cls) == types.ClassType
    assert issubclass(state_cls, State)
    self._state_insts[state_cls] = state_cls(self)

  def StateInstance(self, state_cls):
    assert type(state_cls) == types.ClassType
    assert issubclass(state_cls, State)
    return self._state_insts.get(state_cls)

  def _NextState(self, event):
    state_cls = self._state_machine.GetTransition(self._current_state, event)
    if not state_cls:
      return None
    return state_cls

  def _HandleEvent(self, event):
    next_state_cls = self._NextState(event)
    if next_state_cls is not None:
      self._DoTransition(event, self._current_state, next_state_cls)
    else:
      self._DoNoTransition(event, self._current_state)

  def _DoTransition(self, event, from_state_cls, to_state_cls):
    from_state = self.StateInstance(from_state_cls)
    to_state = self.StateInstance(to_state_cls)

    from_state.TransitionOut(event)
    self._current_state = to_state_cls
    to_state.TransitionIn(event)
    self.PushEvent(StateMachine.EVENT.Unconditional)

  def _DoNoTransition(self, event, state):
    self.CurrentState().NoTransition(event)


class State:
  def __init__(self, sm):
    self._sm = sm
    self._enter_count = 0L
    self._exit_count = 0L

  def EnterCount(self):
    return self._enter_count

  def ExitCount(self):
    return self._exit_count

  def TransitionIn(self, event):
    self._enter_count += 1

  def TransitionOut(self, event):
    self._exit_count += 1

  def NoTransition(self, event):
    """ Called when an event does not result in a transition """
    pass


class StateMachine:
  EVENT = util.Enum(*(
    ('Unconditional', -1),
  ))

  TRANSITIONS = {}

  def GetTransition(self, from_state, event):
    events = self.TRANSITIONS.get(from_state)
    if not events:
      return None
    return events.get(event)

  def IterVerticies(self):
    return self.TRANSITIONS.iteritems()

  class InitialState(State):
    pass
