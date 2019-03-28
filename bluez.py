"""Swith the LEDs on over bluetooth via BlueZ"""

from __future__ import print_function

import time

from pydbus import SystemBus, Variant

from populele import Populele

#pylint: disable=unused-import
from animations import k2000
from animations import pong
from animations import scroll
#pylint: enable=unused-import

#pylint: disable=useless-object-inheritance

# This is the OTA firmware update service, which is advertised by DA14580
# There may be some other way to be more precise when identifying the Populele
DIALOG_UUID = '0000fef5-0000-1000-8000-00805f9b34fb'

# Global vars are bad, maybe.
DBUS = SystemBus()
MANAGER = DBUS.get('org.bluez', '/')

def GetBitInByte(byte, index):
  """Helper method to get the state of a bit in a byte.

  Args:
    byte(byte): the byte to change.
    index(int): the byte position

  Returns:
    bool: wheter the bit is 1
  """
  return byte >> index & 1

def SetBitInByte(byte, index, val):
  """Helper method to change the state of a bit in a byte.

  Args:
    byte(byte): the byte to change.
    index(int): the byte position
    val(bool): whether to set it to 1 or 0

  Returns:
    byte: the result byte.
  """
  index = index % 8
  mask = 1 << index
  byte &= ~mask
  if val:
    byte |= mask
  return byte

class BlueZPopulele(Populele):
  """A class for a Populele Object"""

  POPULELE_CMD = bytearray([0xF1])
  POPULELE_TAIL = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
  GATT_WRITE_SERVICE_UUID = '0000dc86-0000-1000-8000-00805f9b34fb'

  def __init__(self, bluez_device):
    """Instantiate a BlueZPopulele object.

    Args:
      bluez_device(DBUS): the pydbus object representing a Bluetooth device
        for the Populele
    """
    super(BlueZPopulele, self).__init__()
    self._device = bluez_device
    self._write_service = None
    self._state = [
        bytearray([0x00, 0x00, 0x00]),
        bytearray([0x00, 0x00, 0x00]),
        bytearray([0x00, 0x00, 0x00]),
        bytearray([0x00, 0x00, 0x00])
        ]


  def Setup(self):
    """Connects to the Populele via bluetooth."""
    self._Connect()
    if not self._write_service:
      raise Exception(
          'Could not set up GATT services.\n'
          'This could be because we detected a Dialog Bluetooth device that '
          'is not a Populele')
    self.ShowFrame()

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

    if x > 9:
      cur_byte = self._state[y][0]
      return GetBitInByte(cur_byte, x - 10)

    if x > 1:
      cur_byte = self._state[y][1]
      return GetBitInByte(cur_byte, x - 2)

    cur_byte = self._state[y][2]
    return GetBitInByte(cur_byte, x + 6)

  def _Connect(self):
    """Connect to the Bluetooth device"""
    while not self._device.Connected:
      print('Trying to connect')
      self._device.Connect()
      time.sleep(0.2)
    print('connected!')

    while not self._device.ServicesResolved:
      print('Waiting for services to be resolved')
      time.sleep(0.5)
    self._SetupServices()

  def _SetupServices(self):
    """Searches for the GATT service we want to use."""
    objects = MANAGER.GetManagedObjects()
    for path in objects:
      interface = objects[path]
      if interface.get('org.bluez.GattCharacteristic1'):
        gatt = DBUS.get('org.bluez', path)
        if gatt.UUID.lower() == self.GATT_WRITE_SERVICE_UUID.lower():
          self._write_service = gatt

  def Write(self, value):
    """Sends a command to the Bluetooth device.

    Args:
      value(bytearray): the raw data to send to the GATT service.
    """
    self._write_service.WriteValue(value, {'Type': Variant('s', 'command')})

  def ShowFrame(self):
    """Displays the state of the LEDs on the Populele fretboard."""
    # strings are G C E A (A being row 0)
    val = self._state[3] + self._state[2] + self._state[1] + self._state[0]
    self.Write(self.POPULELE_CMD + val + self.POPULELE_TAIL)

  def SetAll(self, value):
    """Sets all the pixels in the frame to the same value.

    Args:
      value(byte): the PWM value.
    """
    if value == 0x00:
      self._state = [
          bytearray([0x00, 0x00, 0x00]),
          bytearray([0x00, 0x00, 0x00]),
          bytearray([0x00, 0x00, 0x00]),
          bytearray([0x00, 0x00, 0x00]),
          ]
    else:
      self._state = [
          # We don't use value's value here, as over bluetooth we can only set
          # On or Off state.
          bytearray([0xFF, 0xFF, 0xFF]),
          bytearray([0xFF, 0xFF, 0xFF]),
          bytearray([0xFF, 0xFF, 0xFF]),
          bytearray([0xFF, 0xFF, 0xFF]),
          ]

  def SetPixel(self, x, y, value):
    """Sets a Pixel to a value in the frame

    Args:
      x(int): coordinate along the frets (0 to 17)
      y(int): coordinate along the strings (0 to 3)
      value(byte): the PWM brightness value
    """
    if x > 9:
      cur_byte = self._state[y][0]
      new_byte = SetBitInByte(cur_byte, x - 10, value != self.LED_OFF)
      self._state[y][0] = new_byte
    elif x > 1:
      cur_byte = self._state[y][1]
      new_byte = SetBitInByte(cur_byte, x - 2, value != self.LED_OFF)
      self._state[y][1] = new_byte
    else:
      cur_byte = self._state[y][2]
      new_byte = SetBitInByte(cur_byte, x + 6, value != self.LED_OFF)
      self._state[y][2] = new_byte

  def DebugFrame(self):
    """Prints the state of the frame to the console"""
    print('\n'.join([
        ''.join(
            ["{0:08b}".format(b) for b in i]
        ) for i in self._state]))

class BlueZDbus(object):
  """Helper class to talk to Bluez services over DBus"""

  def __init__(self):
    self.adapter = None

  def SetUp(self):
    """Sets up the Bluetooth adapter"""
    try:
      self.adapter = self._GetFirstAdapter()
    except KeyError:
      pass
    if not self.adapter:
      raise Exception('Could not find Bluez adapter. Turn bluetooth on maybe?')

    print('Adapter address: {0}'.format(self.adapter.Address))
    if not self.adapter.Powered:
      print('Switching adapter on')
      self.adapter.Powered = True

    for known_device in self.GetKnownDevices():
      print('Deleting known device {0}'.format(known_device.Address))
      known_device.Disconnect()
      self.adapter.RemoveDevice(
          '/org/bluez/hci0/dev_'+known_device.Address.replace(':', '_'))

    self.adapter.SetDiscoveryFilter({})

    while self.adapter.Discovering:
      print('Waiting for adapter to stop discovering')
      self.adapter.StopDiscovery()
      time.sleep(0.5)

  def GetKnownDevices(self):
    """Lists Bluez Devices.

    Returns:
      list(DBus): a list of DBus BLuez Device objects.
    """
    objects = MANAGER.GetManagedObjects()
    res = []
    for path in objects:
      interface = objects[path]
      if interface.get('org.bluez.Device1'):
        known_device = DBUS.get('org.bluez', path)
        res.append(known_device)
    return res

  def _GetFirstAdapter(self):
    """Returns the first Bluez Bluetooth adapter.

    Returns:
      DBus: the adapter DBus object.
    """
    adapter = DBUS.get('org.bluez', '/org/bluez/hci0')
    return adapter

  def SearchDeviceWithUUID(self, uuid):
    """Searches for the first bluetooth devices that expose a service UUID.

    Args:
      uuid(str): the uuid to search. ex: '0000fef5-0000-1000-8000-00805f9b34fb'
    Returns:
      DBus: a DBus device.
    """
    self.adapter.StartDiscovery()
    try:
      while True:
        for known_device in self.GetKnownDevices():
          if uuid in known_device.UUIDs:
            return known_device
        time.sleep(0.5)
        print('Searching for Populele')
    finally:
      self.adapter.StopDiscovery()
      time.sleep(0.2)


# Set up bluetooth adapter
bluez_helper = BlueZDbus()
bluez_helper.SetUp()

# Find the Populele
populele = BlueZPopulele(bluez_helper.SearchDeviceWithUUID(DIALOG_UUID))
populele.Setup()

animation = scroll.ScrollAnimator(populele)

while True:
  #populele.DebugFrame()
  animation.Draw()
  populele.ShowFrame()
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
