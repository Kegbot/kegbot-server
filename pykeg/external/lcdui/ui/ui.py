import datetime
import Queue
import threading
import time

class LcdUi:
  def __init__(self, lcd):
    self._lcd = lcd 
    self._frame_stack = []

    self._last_paint = None
    self._key_events = Queue.Queue()
    self._last_activity = datetime.datetime.now()
    self._max_idle = datetime.timedelta(seconds=8)
    self._is_idle = False

    self._quit = threading.Event()

  def Activity(self):
    self._last_activity = datetime.datetime.now()
    self._SetIdle(False)

  def HandleKeyEvent(self, event):
    self.Activity()

  def Repaint(self):
    """Redraw the screen with the current frame"""
    self._DoRepaint()

  def PushFrame(self, frame):
    """Add a frame to the top of the stack and set as current"""
    self._frame_stack.append(frame)

  def PopFrame(self):
    """Remote the topmost frame on the stack and set new current frame.

    If the stack is empty as a result of the pop, a psuedoframe consisting of
    the blank screen will be drawn. If the stack is already empty, an exception
    is raised.
    """
    if not self._frame_stack:
      return
    ret = self._frame_stack[-1]
    self._frame_stack = self._frame_stack[:-1]
    return ret

  def SetFrame(self, frame):
    """Clear the stack of frames and set |frame| to current"""
    self._frame_stack = [frame]

  def CurrentFrame(self):
    if len(self._frame_stack):
      return self._frame_stack[-1]
    else:
      return None

  def FrameFactory(self, frame_cls, **kwargs):
    return frame_cls(rows=self._lcd.rows(), cols=self._lcd.cols(), **kwargs)

  def MainLoop(self):
    self._lcd.ClearScreen()
    self._lcd.BacklightEnable(True)
    while not self._quit.isSet():
      self.StepLoop()
      time.sleep(0.1)

  def StepLoop(self):
    # set idle if needed
    self._CheckActivity()

    # handle key inputs if needed
    self._HandleKeyEvents()

    # repaint as neede
    self._DoRepaint()

  def _DoRepaint(self):
    current_frame = self.CurrentFrame()
    current_buffer = None

    if current_frame is not None:
      current_buffer = current_frame.Paint().array()
      current_str = current_buffer.tostring()

    if current_str != self._last_paint:
      self._last_paint = current_str
      if current_buffer is None:
        self._lcd.ClearScreen()
      else:
        self._lcd.WriteScreen(current_buffer)

  def _HandleKeyEvents(self):
    while True:
      try:
        event = self._key_events.get_nowait()
      except Queue.Empty:
        return

      current_frame = self.CurrentFrame()
      if current_frame:
        current_frame.HandleKeyEvent(event)

  def _CheckActivity(self):
    now = datetime.datetime.now()
    activity_delta = now - self._last_activity

    if activity_delta > self._max_idle:
      self._SetIdle(True)

  def _SetIdle(self, is_idle):
    if is_idle:
      if not self._is_idle:
        self._lcd.BacklightEnable(False)
        self._is_idle = True
    else:
      if self._is_idle:
        self._lcd.BacklightEnable(True)
        self._is_idle = False

