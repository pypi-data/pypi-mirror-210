# -*- coding: utf-8 -*-


from brainpy._src.context import share
from brainpy import math as bm, check
from .base import Layer

__all__ = [
  'Dropout'
]


class Dropout(Layer):
  """A layer that stochastically ignores a subset of inputs each training step.

  In training, to compensate for the fraction of input values dropped (`rate`),
  all surviving values are multiplied by `1 / (1 - rate)`.

  This layer is active only during training (`mode=brainpy.modes.training`). In other
  circumstances it is a no-op.

  Parameters
  ----------
  prob : float
    Probability to keep element of the tensor.
  seed : optional, int
    The random sampling seed.
  mode: Mode
    The computation mode of the object.
  name : str, optional
    The name of the dynamic system.

  References
  ----------
  .. [1] Srivastava, Nitish, et al. "Dropout: a simple way to prevent
         neural networks from overfitting." The journal of machine learning
         research 15.1 (2014): 1929-1958.
  """

  def __init__(
      self,
      prob: float,
      seed: int = None,
      mode: bm.Mode = None,
      name: str = None
  ):
    super(Dropout, self).__init__(mode=mode, name=name)
    self.prob = check.is_float(prob, min_bound=0., max_bound=1.)
    self.rng = bm.random.default_rng(seed)

  def update(self, x):
    if share.load('fit'):
      keep_mask = self.rng.bernoulli(self.prob, x.shape)
      return bm.where(keep_mask, x / self.prob, 0.)
    else:
      return x

