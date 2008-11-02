#!/usr/bin/env python
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

"""Unittest for StateMachine module"""

import unittest
import util
import StateMachine

class ExampleMachine(StateMachine.StateMachine):
  class NormalState(StateMachine.State):
    pass

  class AlarmState(StateMachine.State):
    pass

  class FailState(StateMachine.State):
    pass

  EVENT = util.Enum(*(
    'Alarm',
    'Failure',
    'ClearAlarm',
    'Restart',
  ))

  TRANSITIONS = {
      StateMachine.StateMachine.InitialState : {
        StateMachine.StateMachine.EVENT.Unconditional : NormalState,
      },
      NormalState : {
        EVENT.Alarm : AlarmState,
        EVENT.Failure : FailState,
      },
      AlarmState : {
        EVENT.ClearAlarm : NormalState,
        EVENT.Failure : FailState,
        EVENT.Restart : NormalState,
      },
      FailState : {
        EVENT.Restart : NormalState,
      },
  }

class DriverTestCase(unittest.TestCase):
  def setUp(self):
    self.smd = StateMachine.StateMachineDriver(ExampleMachine())

  def testBasicLogic(self):
    """Test transition logic, without involving the event queue"""
    for k, v in self.smd._state_machine.IterVerticies():
      print k, v

    self.assertEquals(self.smd.CurrentStateCls(),
                      ExampleMachine.InitialState)

    # Initial event
    self.smd._HandleEvent(StateMachine.StateMachine.EVENT.Unconditional)
    self.assertEquals(self.smd.CurrentStateCls(),
                      ExampleMachine.NormalState)

    # Check state instance counters
    st = self.smd.StateInstance(ExampleMachine.NormalState)
    self.assertEquals(st.EnterCount(), 1)
    self.assertEquals(st.ExitCount(), 0)

    # Spurious event
    self.smd._HandleEvent(StateMachine.StateMachine.EVENT.Unconditional)
    self.assertEquals(self.smd.CurrentStateCls(),
                      ExampleMachine.NormalState)

    # NormalState -> AlarmState
    self.smd._HandleEvent(ExampleMachine.EVENT.Alarm)
    self.assertEquals(self.smd.CurrentStateCls(),
                      ExampleMachine.AlarmState)

    # AlarmState -> NormalState
    self.smd._HandleEvent(ExampleMachine.EVENT.ClearAlarm)
    self.assertEquals(self.smd.CurrentStateCls(),
                      ExampleMachine.NormalState)

    # NormalState -> FailState
    self.smd._HandleEvent(ExampleMachine.EVENT.Failure)
    self.assertEquals(self.smd.CurrentStateCls(),
                      ExampleMachine.FailState)

    # FailState
    self.smd._HandleEvent(ExampleMachine.EVENT.ClearAlarm)
    self.assertEquals(self.smd.CurrentStateCls(),
                      ExampleMachine.FailState)

    # FailState -> NormalState
    self.smd._HandleEvent(ExampleMachine.EVENT.Restart)
    self.assertEquals(self.smd.CurrentStateCls(),
                      ExampleMachine.NormalState)

    # Check counters
    st = self.smd.StateInstance(ExampleMachine.NormalState)
    self.assertEquals(st.EnterCount(), 3)
    self.assertEquals(st.ExitCount(), 2)

  def testEventQueue(self):
    # The machine starts off in the initial state, with a single unconditional
    # event on the queue.
    q = self.smd._event_queue
    self.assertEquals(self.smd.CurrentStateCls(),
                      ExampleMachine.InitialState)

    self.assert_(not q.empty())
    ev = q.get_nowait()
    self.assertEquals(ev, StateMachine.StateMachine.EVENT.Unconditional)

    # The event queue should now be empty.
    self.assert_(q.empty())

    # Process the unconditional event. This should cause transition to the first
    # real state.
    self.smd._HandleEvent(ev)
    self.assertEquals(self.smd.CurrentStateCls(), ExampleMachine.NormalState)

    # A transition pushes a new unconditional event on the queue.
    self.assert_(not q.empty())
    ev = q.get_nowait()
    self.assertEquals(ev, StateMachine.StateMachine.EVENT.Unconditional)

    # The ExampleMachine transition table should cause this event to be dropped.
    self.smd._HandleEvent(ev)
    self.assertEquals(self.smd.CurrentStateCls(), ExampleMachine.NormalState)

    # Because no transition happened, the event queue should once again be
    # empty.
    self.assert_(q.empty())


if __name__ == '__main__':
  unittest.main()
