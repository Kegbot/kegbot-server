class ICharacterDisplay(object):
  def rows(self):
    """Total number of lines"""
    raise NotImplementedError

  def cols(self):
    """Total number of characters in a line"""
    raise NotImplementedError

  def ClearScreen(self):
    """Blank the screen"""
    raise NotImplementedError

  def BacklightEnable(self, enable):
    """Enable or disable the backlight.

    Args
      enable - True to enable, False to disable

    Returns
      None
    """
    raise NotImplementedError

  def SetCursor(self, row, col):
    """Place the cursor at location (row,col)

    Args:
      row - vertical position (zero-indexed)
      col - horizontal position (zero-indexed)
    """
    raise NotImplementedError

  def WriteData(self, data, row, col):
    """Write data starting at given position.

    Args
      data - an iterable containing characters
      row - starting line
      col - starting offset on row

    Returns
      None
    """
    raise NotImplementedError

  def WriteScreen(self, data):
    raise NotImplementedError
