import sys
from plasTeX.TeX import TeX
from plasTeX.Renderers.HTML5 import Renderer
Renderer().render(TeX(file=sys.argv[-1]).parse())
