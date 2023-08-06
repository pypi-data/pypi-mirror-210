import sys
from print_tools import pp, ppd
from path_tools import resolve, resolve_dir, parent
sys.path.insert(0,'/Users/mfsteele/Git/dotspace/src/dotspace')
from dots import Dots
ds = Dots(**dict(testa='a',test1=1))