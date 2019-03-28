"""TODO"""
from __future__ import print_function

import time

from pydbus import SystemBus, Variant

#pylint: disable=unused-import
from animations import k2000
from animations import pong
from animations import scroll
#pylint: enable=unused-import


DIALOG_UUID = '0000fef5-0000-1000-8000-00805f9b34fb'

DBUS = SystemBus()
MANAGER = DBUS.get('org.bluez', '/')

class BlueZPopulele(object):
  """TODO"""
  POPULELE_CMD = bytearray([0xf1])
  POPULELE_TAIL = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
  GATT_WRITE_SERVICE_UUID = '0000dc86-0000-1000-8000-00805f9b34fb'

  def __init__(self, bluez_device):
    """todo"""
    self.device = bluez_device
    self.write_service = None
    self.state = [
        bytearray([0x00, 0x00, 0x00]),
        bytearray([0x00, 0x00, 0x00]),
        bytearray([0x00, 0x00, 0x00]),
        bytearray([0x00, 0x00, 0x00]),
        ]

  def Connect(self):
    """TODO"""
    while not self.device.Connected:
      self.device.Connect()
    print('connection state: {0}'.format(self.device.Connected))
    while not self.device.ServicesResolved:
      print('Waiting to resolve services')
      time.sleep(1)
    self.ResolveServices()
    self.ShowFrame()

  def ResolveServices(self):
    """TODO"""
    objects = MANAGER.GetManagedObjects()
    for path in objects:
      interface = objects[path]
      if interface.get('org.bluez.GattCharacteristic1'):
        gatt = DBUS.get('org.bluez', path)
        if gatt.UUID == self.GATT_WRITE_SERVICE_UUID:
          self.write_service = gatt

  def Write(self, value):
    """TODO"""
    self.write_service.WriteValue(value, {'Type': Variant('s', 'command')})

  def ShowFrame(self):
    """TODO"""
    val = self.state[0] + self.state[1] + self.state[2] + self.state[3]
    self.Write(self.POPULELE_CMD + val + self.POPULELE_TAIL)

  def SetAll(self, val):
    """Sets all the pixels in the frame to the same value.

    Args:
      val(byte): the PWM value.
    """
    if val == 0x00:
      self.state = [
          bytearray([0x00, 0x00, 0x00]),
          bytearray([0x00, 0x00, 0x00]),
          bytearray([0x00, 0x00, 0x00]),
          bytearray([0x00, 0x00, 0x00]),
          ]
    else:
      self.state = [
          bytearray([0xFF, 0xFF, 0xFF]),
          bytearray([0xFF, 0xFF, 0xFF]),
          bytearray([0xFF, 0xFF, 0xFF]),
          bytearray([0xFF, 0xFF, 0xFF]),
          ]

  def SetCol(self, the_byte, position, value=0x00):
    """Sets a 'column' (all 4 strings for a fret position).

    Args:
      the_byte(byte): the state of the columnt (bit pos = LED status).
      position(int): which column to set.
      value(byte): the PWM brightness value
    """
    if position < 0:
      return
    if position > 17:
      return
    byte = the_byte & 0x0F
    for xx in range(4):
      val = 0xFF if (byte & 1) else 0x00
      self.SetPixel(position if xx < 4 else position+1, xx, val)
      byte = byte >> 1

  def _SetBitInByte(self, byte, index, val):
    mask = 1 << index
    byte &= ~mask
    if val:
      byte |= mask
    return byte

  def SetPixel(self, x, y, val):
    """Sets a Pixel to a value in the frame

    Args:
      x(int): coordinate along the frets (0 to 17)
      y(int): coordinate along the strings (0 to 3)
      val(byte): the PWM brightness value
    """
    if x > 9:
      cur_byte = self.state[y][0]
      new_byte = self._SetBitInByte(cur_byte, x - 10, val != 0x00)
      self.state[y][0] = new_byte
    elif x > 1:
      cur_byte = self.state[y][1]
      new_byte = self._SetBitInByte(cur_byte, x - 2, val != 0x00)
      self.state[y][1] = new_byte
    else:
      cur_byte = self.state[y][2]
      new_byte = self._SetBitInByte(cur_byte, x + 6, val != 0x00)
      self.state[y][2] = new_byte

  def DebugFrame(self):
    """TODO"""
    print('\n'.join([
        ''.join(
            ["{0:08b}".format(b) for b in i]
        ) for i in self.state]))


class BlueZDbus(object):
  """Todo"""

  def __init__(self):
    self.adapter = None

  def SetUp(self):
    """TODO"""
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

#    for known_device in self.GetKnownDevices():
#      print('Deleting known device {0}'.format(known_device.Address))
#      self.adapter.RemoveDevice(
#          '/org/bluez/hci0/dev_'+known_device.Address.replace(':', '_'))

    self.adapter.SetDiscoveryFilter({})

    while self.adapter.Discovering:
      print('Waiting for adapter to stop discovering')
      self.StopDiscovery()
      time.sleep(0.5)

  def GetKnownDevices(self):
    """todo"""
    objects = MANAGER.GetManagedObjects()
    res = []
    for path in objects:
      interface = objects[path]
      if interface.get('org.bluez.Device1'):
        known_device = DBUS.get('org.bluez', path)
        res.append(known_device)
    return res

  def _GetFirstAdapter(self):
    """todo"""
    adapter = DBUS.get('org.bluez', '/org/bluez/hci0')
    return adapter

  def StartDiscovery(self):
    """todo"""
    print("Starting Discovery")
    self.adapter.StartDiscovery()

  def StopDiscovery(self):
    """todo"""
    print("Stopping Discovery")
    self.adapter.StopDiscovery()

  def SearchDeviceWithUUID(self, uuid):
    """todo"""
    b.StartDiscovery()
    try:
      while True:
        for known_device in self.GetKnownDevices():
          if uuid in known_device.UUIDs:
            return BlueZPopulele(known_device)
        time.sleep(0.5)
        print('Waiting for Populele')
    finally:
      b.StopDiscovery()
      time.sleep(0.2)


b = BlueZDbus()
b.SetUp()
populele = b.SearchDeviceWithUUID(DIALOG_UUID)
populele.Connect()

animation = k2000.K2000Animator(populele)
while True:
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
