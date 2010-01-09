import array

class Frame(object):
  def __init__(self, rows, cols):
    self._rows = rows
    self._cols = cols
    self._widget = {}
    self._position = {}
    self._span = {}
    self._screen_buffer = ScreenBuffer(self._rows, self._cols)

  def AddWidget(self, name, widget, row=0, col=0, span=None):
    self._widget[name] = widget
    self._position[name] = (row, col)
    self._span[name] = span or max(0, self._cols - col)

  def GetWidget(self, name):
    return self._widget.get(name)

  def RemoveWidget(self, name):
    del self._widget[name]
    del self._position[name]
    del self._span[name]

  def Paint(self):
    for widgetname, widget in self._widget.iteritems():
      outstr = widget.Update()
      row, col = self._position[widgetname]
      span = self._span[widgetname]
      self._screen_buffer.Write(array.array('c', outstr), row, col, span)
    return self._screen_buffer

  def SwitchInEvent(self):
    pass

  def SwitchOutEvent(self):
    pass


class ScreenBuffer:
   def __init__(self, rows, cols):
      self._rows = rows
      self._cols = cols
      self._array = array.array('c', [' '] * (rows * cols))

   def __eq__(self, other):
      if isinstance(other, ScreenMatrix):
         return self._array == other._array
      return False

   def array(self):
     return self._array

   def _AllocNewArray(self):
     return array.array('c', [' '] * (self._rows * self._cols))

   def _GetOffset(self, row, col):
     return row*self._cols + col

   def Clear(self):
     self._array = self._AllocNewArray()

   def Write(self, data, row, col, span):
      """ replace data at row, col in this matrix """
      assert row in range(self._rows)
      assert col in range(self._cols)

      start = self._GetOffset(row, col)
      datalen = min(len(data), span)
      end = start + datalen
      self._array[start:end] = data[:datalen]

   def __str__(self):
      return self._array.tostring()
