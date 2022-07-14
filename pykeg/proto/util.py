class AttrDict(dict):
  """Dict that exposes items as attributes.

  Source: https://stackoverflow.com/a/48806603
  """

  def __init__(self, mapping=None):
    super(AttrDict, self).__init__()
    if mapping is not None:
      for key, value in mapping.items():
        self.__setitem__(key, value)

  def __setitem__(self, key, value):
    if isinstance(value, dict):
      value = AttrDict(value)
    super(AttrDict, self).__setitem__(key, value)
    self.__dict__[key] = value  # for code completion in editors

  def __getattr__(self, item):
    try:
      return self.__getitem__(item)
    except KeyError:
      raise AttributeError(item)

  __setattr__ = __setitem__
