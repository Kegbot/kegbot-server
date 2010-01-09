class Widget:
  def __init__(self):
    pass

  def GetString(self):
    return ''

  def Update(self):
    return self._GetString()


class LineWidget(Widget):
  def __init__(self, contents='', prefix='', postfix=''):
    Widget.__init__(self)
    self._contents = contents
    self._prefix = prefix
    self._postfix = postfix

  def _GetString(self):
    ret = self._prefix + self._contents + self._postfix
    return ret

  def set_contents(self, s):
    self._contents = s
  def contents(self): return self._contents

  def set_prefix(self, s):
    self._prefix = prefix
  def prefix(self): return self._prefix

  def set_postfix(self, s):
    self._postfix = s
  def postfix(self): return self._postfix
