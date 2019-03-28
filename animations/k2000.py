"""Animator for K2000 effect."""

from animations import Animator

class K2000Animator(Animator):
  """Animator for a K2000 effect."""

  def __init__(self, *args, **kwargs):
    """Initializes a K2000Animator object."""
    super(K2000Animator, self).__init__(*args, **kwargs)

    self.interval = 50
    self._column = 0
    self.leftright = True
    self.led_on = self._populele.LED_ON
    self.led_off = self._populele.LED_OFF

  def Draw(self):
    self._populele.SetAll(self.led_off)
    self._populele.SetCol(0x0F, self._column-2, value=0x10)
    self._populele.SetCol(0x0F, self._column-1, value=0x20)
    self._populele.SetCol(0x0F, self._column, value=0x55)
    self._populele.SetCol(0x0F, self._column+1, value=0x20)
    self._populele.SetCol(0x0F, self._column+2, value=0x10)


    if self.leftright:
      self._column += 1
      if self._column >= 18:
        self.leftright = False
    else:
      self._column -= 1
      if self._column <= 0:
        self.leftright = True
