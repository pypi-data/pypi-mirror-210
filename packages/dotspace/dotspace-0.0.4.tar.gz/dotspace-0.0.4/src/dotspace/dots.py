from types import SimpleNamespace

class Dots(SimpleNamespace):
  def __init__(self, *args, **kw):
    super().__init__(**kw)
    self.args = list(args)
    for k,v in kw.items():
      if isinstance(v,tuple,list):
        self.k.update( dict(args=v) )