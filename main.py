"""Main script"""

import time
import board
import busio

from digitalio import DigitalInOut, Direction

# Doc:
# https://circuitpython.readthedocs.io/en/3.x/shared-bindings/busio/I2C.html
# https://circuitpython.readthedocs.io/projects/busdevice/en/latest/api.html

# pylint: disable=consider-using-enumerate

# pylint: disable=undefined-variable
POPULELE_I2C_ADDR = const(0x74)
POPULELE_NB_LEDS = const(144)

POPULELE_BASE_LED = 0x24

LED_ON = const(0x55)
LED_OFF = const(0x00)
# pylint: enable=undefined-variable

# pylint: disable=line-too-long
# These are the addresses of each LED
STRINGS = [
    # A
    bytes([39, 40, 55, 56, 71, 72, 87, 88, 103, 104, 119, 120, 135, 136, 151, 152, 143, 144]),
    # E
    bytes([38, 41, 54, 57, 70, 73, 86, 89, 102, 105, 118, 121, 134, 137, 150, 153, 142, 145]),
    # C
    bytes([37, 42, 53, 58, 69, 74, 85, 90, 101, 106, 117, 122, 133, 138, 149, 154, 141, 146]),
    # G
    bytes([36, 43, 52, 59, 68, 75, 84, 91, 100, 107, 116, 123, 132, 139, 148, 155, 140, 147])
]
# pylint: enable=line-too-long

FONT3x4 = {
    # One byte per 'column' of pixels
    'A': [0x7, 0xA, 0x7],
    'O': [0x6, 0x9, 0x6],
    'W': [0xF, 0x2, 0xF],
    '!': [0xD],
    ' ': [0x0, 0x0, 0x0]
}

class Populele():
  """Class for a Populele"""

  def __init__(self):
    """Initializes the Populele i2c"""
    i2c = busio.I2C(board.SCL, board.SDA)
    self.i2c = i2c

    self.frame_1 = bytearray('\00'*POPULELE_NB_LEDS)

  def SetAll(self, val):
    """Sets all the pixels in the frame to the same value.

    Args:
      val(byte): the PWM value.
    """
    frame = self.frame_1
    for i in range(len(frame)):
      frame[i] = val

  def ShowFrame(self):
    """Displays the state of the frame on the board."""
    while not self.i2c.try_lock():
      pass
    try:
      self.i2c.writeto(
          POPULELE_I2C_ADDR, bytes([POPULELE_BASE_LED])+self.frame_1)
    finally:
      self.i2c.unlock()

  def _Send(self, buff):
    """Sends a buffer to the led Matrix.

    Args:
      buff(list): list of bytes to send.
    """
    self.i2c.writeto(POPULELE_I2C_ADDR, bytes(buff))

  def Init(self):
    """Sends the LED matrix initalization sequence."""
    while not self.i2c.try_lock():
      pass
    try:
      send = self._Send
        # Open Page Nine, Function register
      send([0xFD, 0x0B])
          # shutdown = true
      send([0x0A, 0x00])
          # Open page 1
      send([0xFD, 0x00])
          # configure all LEDs in matrix A
      send([0x00, 0xFF])
      send([0x02, 0xFF])
      send([0x04, 0xFF])
      send([0x06, 0xFF])
      send([0x08, 0xFF])
      send([0x0A, 0xFF])
      send([0x0C, 0xFF])
      send([0x0E, 0xFF])
      send([0x10, 0x00]) # except CA9
          # Unconfigure all LED in matrix B
      send([0x01, 0x00])
      send([0x03, 0x00])
      send([0x05, 0x00])
      send([0x07, 0x00])
      send([0x09, 0x00])
      send([0x0B, 0x00])
      send([0x0D, 0xFF]) # Except CB7
      send([0x0F, 0x00])
      send([0x11, 0x00])

      # Set picture mode
      send([0xFD, 0x0B])
      send([0x00, 0x00])

      # Undo shutdown
      send([0xFD, 0x0B])
      send([0x0A, 0x01])

      send([0xFD, 0x00])
      # Clear everything
      self._All(LED_OFF)

    finally:
      self.i2c.unlock()

  def DebugFrame(self):
    """Prints the state of the frame to the console"""
    frame = self.frame_1
    for string in range(4):
      res = ""
      for x in range(18):
        res += str(frame[STRINGS[string][x] - POPULELE_BASE_LED])+', '
      print(res)

  def TogglePixel(self, x, y):
    """Changes the state of one pixel from ON to OFF.

    Args:
      x(int): coordinate along the frets (0 to 17)
      y(int): coordinate along the strings (0 to 3)
    """
    index = STRINGS[y][(17-x)%18] - POPULELE_BASE_LED
    curr_val = self.frame_1[index]
    val = LED_ON if (curr_val == LED_OFF) else LED_OFF
    self.frame_1[index] = val

  def SetPixel(self, x, y, val):
    """Sets a Pixel to a value in the frame

    Args:
      x(int): coordinate along the frets (0 to 17)
      y(int): coordinate along the strings (0 to 3)
      val(byte): the PWM brightness value
    """
    index = STRINGS[y][(17-x)%18]
    self.frame_1[index - POPULELE_BASE_LED] = val

  def _All(self, val):
    """Sets the same PWM brightness value to all LEDs

    Args:
      val(byte): the PWM brightness value.
    """
    for a in range(POPULELE_NB_LEDS):
      self.i2c.writeto(POPULELE_I2C_ADDR, bytes([a + POPULELE_BASE_LED, val]))

  def SetCol(self, the_byte, position):
    """Sets a 'column' (all 4 strings for a fret position).

    Args:
      the_byte(byte): the state of the columnt (bit pos = LED status).
      position(int): which column to set.
    """
    if position > 17:
      return
    byte = the_byte & 0x0F
    for x in range(4):
      val = LED_ON if (byte & 1) else LED_OFF
      self.SetPixel(position if x < 4 else position+1, x, val)
      byte = byte >> 1

  def SetChar(self, char, position):
    """Displays an ASCII character at a position.

    Args:
      char(list): list of nibbles that display a character.
      position(int): at which X position to display it.

    Returns:
      int: the number of columns set.
    """
    cc = FONT3x4.get(char, [0x00])
    i = 0
    for c in cc:
      if position+i <= 17:
        self.SetCol(c & 0x0F, position+i)
      i += 1
    return i

  def SetString(self, string, position, wrap=True):
    """Sets a string of ASCII characters in the frame.

    Args:
      string(list(list(byte)): the characters list.
      position(int): where to start displaying the string.
      wrap(bool): whether we need to wrap back to the beggining.
    """
    p = position
    if wrap:
      p = p % 18
    for char in string:
      size = self.SetChar(char, p)
      p = (p+size+1)
      if wrap:
        p = p % 18

  def SetBytes(self, array, position, wrap=True):
    """Sets a list of nibbles in frame.

    Args:
      array(list(bytes)): the list of nibbles (one per column) to display.
      position(int): where to start displaying the string.
      wrap(bool): whether we need to wrap back to the beggining.
    """
    p = position
    if wrap:
      p = p % 18
    for b in array:
      self.SetCol(b, p)
      p += 1
      if wrap:
        p = p % 18


print("Starting")

sdb = DigitalInOut(board.D10)
sdb.direction = Direction.OUTPUT
sdb.value = False
sdb.value = True
popu = Populele()
popu.Init()

col = 0
scroll_string = (
    FONT3x4[' ']+[0x0]+
    FONT3x4[' ']+[0x0]+
    FONT3x4['A']+[0x0]+
    FONT3x4['W']+[0x0]+
    FONT3x4['O']+[0x0]+
    FONT3x4['O']+[0x0]+
    FONT3x4['!']+
    FONT3x4['!']
)

def Rotate(ss):
  """Rotate the string."""
  return ss[1:]+ss[:1]

while True:
  popu.SetAll(LED_OFF)
  popu.SetBytes(scroll_string, 0, wrap=False)
  popu.ShowFrame()
  scroll_string = Rotate(scroll_string)
  col = (col+1)
  time.sleep(0.1)
