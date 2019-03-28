"""Main script"""

import time
import board
import busio

from digitalio import DigitalInOut, Direction

from populele import Populele

#pylint: disable=unused-import
from animations import k2000
from animations import pong
from animations import scroll
#pylint: enable=unused-import

class SPIPopulele(Populele):
  """Class for a SPI managed Populele"""

  POPULELE_I2C_ADDR = 0x74
  POPULELE_NB_LEDS = 144

  POPULELE_BASE_LED = 0x24
  # pylint: disable=line-too-long
  STRINGS = [
      # These are the addresses of each LED
      # A string
      bytes([39, 40, 55, 56, 71, 72, 87, 88, 103, 104, 119, 120, 135, 136, 151, 152, 143, 144]),
      # E string
      bytes([38, 41, 54, 57, 70, 73, 86, 89, 102, 105, 118, 121, 134, 137, 150, 153, 142, 145]),
      # C string
      bytes([37, 42, 53, 58, 69, 74, 85, 90, 101, 106, 117, 122, 133, 138, 149, 154, 141, 146]),
      # G string
      bytes([36, 43, 52, 59, 68, 75, 84, 91, 100, 107, 116, 123, 132, 139, 148, 155, 140, 147])
  ]
  # pylint: enable=line-too-long

  def __init__(self):
    """Initializes the Populele i2c"""
    i2c = busio.I2C(board.SCL, board.SDA)
    self.i2c = i2c

    self.frame_1 = bytearray('\00'*self.POPULELE_NB_LEDS)

  def SetAll(self, value):
    """Sets all the pixels in the frame to the same value.

    Args:
      value(byte): the PWM value.
    """
    self.frame_1 = bytearray([value]*self.POPULELE_NB_LEDS)

  def ShowFrame(self):
    """Displays the state of the LEDs on the Populele fretboard."""
    while not self.i2c.try_lock():
      pass
    try:
      self.i2c.writeto(
          self.POPULELE_I2C_ADDR, bytes([self.POPULELE_BASE_LED])+self.frame_1)
    finally:
      self.i2c.unlock()

  def _SPISend(self, buff):
    """Sends a buffer to the led Matrix.

    Args:
      buff(list): list of bytes to send.
    """
    self.i2c.writeto(self.POPULELE_I2C_ADDR, bytes(buff))

  def Setup(self):
    """Sends the LED matrix initalization sequence over SPI."""
    while not self.i2c.try_lock():
      pass
    try:
      send = self._SPISend
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
      self._All(self.LED_OFF)

    finally:
      self.i2c.unlock()

  def GetPixel(self, x, y):
    """Get the state of one pixel.

    Args:
      x(int): coordinate along the frets.
      y(int): coordinate along the strings.
    Returns:
      int: the pixel state.
    Raises:
      Exception: if the coordinates are out of bounds.
    """
    if not self.HasPixel(x, y):
      raise Exception('Pixel not found {0:d}, {1:d}'.format(x, y))
    curr_val = self.frame_1[self._GetLedIndex(x, y)]
    return curr_val

  def SetPixel(self, x, y, value):
    """Sets a Pixel to a value in the frame

    Args:
      x(int): coordinate along the frets.
      y(int): coordinate along the strings.
      value(byte): the PWM brightness value.
    """
    self.frame_1[self._GetLedIndex(x, y)] = value

  def _GetLedIndex(self, x, y):
    """Returns the LED matrix index.

    Args:
      x(int): coordinate along the frets.
      y(int): coordinate along the strings.
    Returns:
      int: the address
    Raises:
      Exception: if the coordinates are out of bounds.
    """
    if not self.HasPixel(x, y):
      raise Exception('Pixel not found {0:d}, {1:d}'.format(x, y))
    index = self.STRINGS[y][self.NB_COLS - x - 1]
    return index - self.POPULELE_BASE_LED

  def _All(self, value):
    """Sets the same PWM brightness value to all LEDs via SPI.

    Args:
      value(byte): the PWM brightness value.
    """
    i2c_addr = self.POPULELE_I2C_ADDR
    base_addr = self.POPULELE_BASE_LED
    for a in range(self.POPULELE_NB_LEDS):
      self.i2c.writeto(i2c_addr, bytes([a + base_addr, value]))

print("Starting")

sdb = DigitalInOut(board.D10)
sdb.direction = Direction.OUTPUT
sdb.value = False
sdb.value = True

popu = SPIPopulele()
popu.Setup()

#animation = scroll.ScrollAnimator(popu)
#animation.SetText('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
#animation = k2000.K2000Animator(popu)
animation = pong.PongAnimator(popu)

while True:
  animation.Draw()
#  popu.DebugFrame()
  popu.ShowFrame()
  ival = animation.interval
  while ival > 0:
    # We still have time to do work

    # Run the animation timing
    if ival > 20:
      time.sleep(0.02)
      ival -= 20
    else:
      time.sleep(ival/1000)
      ival = 0
