"""TODO"""

class Animator():
  """Interface for an Animator object.

    Attributes:
      populele(Populele): the populele object to animate.
      interval(int): the number of milliseconds between refreshes.
  """

  def __init__(self, populele, interval=50):
    """Initializes an Animator object

    Args:
      populele(Populele): the Populele object to animate.
      interval(int): the ms between redraws
    """
    self._populele = populele
    self.interval = interval

  def Draw(self):
    """Draws the next frame into the Populele object frame state."""
    raise Exception('Please implement Draw()')
