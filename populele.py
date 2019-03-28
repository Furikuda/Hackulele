"""Populele base object."""

from __future__ import print_function

#pylint: disable=useless-object-inheritance

class Populele(object):
  """Base class for a Populele object."""

  NB_ROWS = 4
  NB_COLS = 18

  LED_ON = 0xFF
  LED_OFF = 0x00

  def ShowFrame(self):
    """Displays the state of the LEDs on the Populele fretboard."""
    raise NotImplementedError('Please implement ShowFrame')

  def SetPixel(self, x, y, value):
    """Sets a Pixel to a value in the frame

    Args:
      x(int): coordinate along the frets.
      y(int): coordinate along the strings.
      value(byte): the PWM brightness value.
    """
    raise NotImplementedError('Please implement SetPixel')

  def GetPixel(self, x, y):
    """Get the state of one pixel.

    Args:
      x(int): coordinate along the frets.
      y(int): coordinate along the strings.
    Returns:
      int: the pixel state.
    """
    raise NotImplementedError('Please implement GetPixel')

  def HasPixel(self, x, y):
    """Returns True if pixel exists."""
    if (0 <= x < self.NB_COLS) and (0 <= y < self.NB_ROWS):
      return True
    return False

  def Setup(self):
    """Does the necessary setup for the underlying physical system."""

  def DebugFrame(self):
    """Prints the state of the frame to the console"""
    # Consider re-implementing something more efficient
    res = ''
    for y in range(self.NB_ROWS):
      for x in range(self.NB_COLS):
        if self.GetPixel(x, y) == self.LED_OFF:
          res += '0'
        else:
          res += '1'
      res += '\n'
    print(res)

  def SetAll(self, value):
    """Sets all the pixels in the frame to the same value.

    Args:
      value(byte): the PWM value.
    """
    # Consider re-implementing something more efficient
    for x in range(self.NB_ROWS):
      for y in range(self.NB_COLS):
        self.SetPixel(x, y, value)

  def SetCol(self, the_byte, position, value=0xFF):
    """Sets a 'column' (all strings for a fret position).

    Args:
      the_byte(byte): Use the last NB_ROWS of the byte to set the state of the
        column (bit position = LED status).
      position(int): which column to set.
      value(byte): the PWM brightness value
    """
    if position < 0:
      # Do nothing
      return
    if position >= self.NB_COLS:
      # Do nothing
      return

    for b in range(self.NB_ROWS):
      val = value if (the_byte & 1) else self.LED_OFF
      self.SetPixel(position, b, val)
      the_byte = the_byte >> 1

  def TogglePixel(self, x, y):
    """Changes the state of one pixel from ON to OFF.

    Args:
      x(int): coordinate along the frets.
      y(int): coordinate along the strings.
    """
    state = self.GetPixel(x, y)
    if state == self.LED_OFF:
      self.SetPixel(x, y, self.LED_ON)
    else:
      self.SetPixel(x, y, self.LED_OFF)

  def SetChar(self, char, font, position):
    """Displays an ASCII character at a position.

    Args:
      char(list): list of nibbles that display a character.
      font(dict): the font to use.
      position(int): at which X position to display it.

    Returns:
      int: the number of columns set.
    """
    cc = font.get(char, [0x00])
    i = 0
    for c in cc:
      if position+i < self.NB_COLS:
        self.SetCol(c, position+i)
      i += 1
    return i

  def SetString(self, string, font, position, wrap=True):
    """Sets a string of ASCII characters in the frame.

    Args:
      string(list(list(byte)): the characters list.
      font(dict): the font to use.
      position(int): where to start displaying the string.
      wrap(bool): whether we need to wrap back to the beggining.
    """
    p = position
    if wrap:
      p = p % self.NB_ROWS
    for char in string:
      size = self.SetChar(char, font, p)
      p = (p+size+1)
      if wrap:
        p = p % self.NB_ROWS
