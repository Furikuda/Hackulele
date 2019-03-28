"""Animator for a scrolling text."""

from animations import Animator
from animations.fonts import FONT3x4


class ScrollAnimator(Animator):
  """Animator for a scrolling text."""

  def __init__(self, *args, **kwargs):
    """Initializes a ScrollAnimation object."""
    super(ScrollAnimator, self).__init__(*args, **kwargs)
    self._scrolldata = [0x00]*16
    self._position = 0
    self.SetFont(FONT3x4)

    self.interval = 200

    self.SetText('AWOO!')

  def SetFont(self, font):
    """Change the font used to display the text.

    Args:
      font(dict): the font to use.
    """

    self._font = font

  def _TextToBytes(self, text):
    res = []
    for c in text:
      res += self._font.get(c, [0xF, 0xF, 0xF]) + [0x00]
    return res

  def SetText(self, text):
    """Set text to display.

    Args:
      text(str): the text to display.
    """
    self._scrolldata += self._TextToBytes(text)

  def Draw(self):
    for x in range(0, self._populele.NB_COLS):
      colbits = self._scrolldata[(self._position + x) % len(self._scrolldata)]
      self._populele.SetCol(colbits, x)
    self._position = (self._position + 1) % len(self._scrolldata)
