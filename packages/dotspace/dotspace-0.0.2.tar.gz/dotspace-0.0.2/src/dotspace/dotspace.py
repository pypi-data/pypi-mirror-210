from types import SimpleNamespace

class Dotspace(SimpleNamespace):
  def __init__(self, *args, **kw: Any) -> None:
    super().__init__(**kw)
    self.args = list(args)
    for k,v in kw.items():
      if isinstance(v,tuple,list):
        self.k.update( dict(args=v) )