"""Animator for Pong effect."""

import random

from animations import Animator

class PongAnimator(Animator):
  """Animator for a Pong effect."""

  def __init__(self, *args, **kwargs):
    """Initializes a PongAnimator object."""
    super(PongAnimator, self).__init__(*args, **kwargs)

    self.interval = 50
    self.updown = 1
    self.leftright = 1
    self.bouncecount = 0
    self.x = random.randrange(0, 18-1)
    self.y = random.randrange(0, 4-1)

  def _Bounce(self):
    nx = self.x + self.leftright
    ny = self.y + self.updown
    if self._populele.HasPixel(nx, ny):
      return

    self.bouncecount += 1
    ## Try a vertical reflection
    if self._populele.HasPixel(nx, self.y - self.updown):
      self.updown = -self.updown
    ## Try a horizontal reflection
    elif self._populele.HasPixel(self.x - self.leftright, ny):
      self.leftright = -self.leftright
    ## Otherwise, come back from whence we came
    else:
      self.updown = -self.updown
      self.leftright = -self.leftright

  def Draw(self):
    self._Bounce()
    self._populele.SetAll(0x00)
    self._populele.SetPixel(self.x, self.y, 0x00)
    self.x += self.leftright
    self.y += self.updown
    self._populele.SetPixel(self.x, self.y, 0xFF)
