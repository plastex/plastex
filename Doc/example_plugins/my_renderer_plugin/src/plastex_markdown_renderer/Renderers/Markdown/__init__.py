from plasTeX.Renderers.PageTemplate import Renderer as PTRenderer

class Renderer(PTRenderer):
    """Renderer targetting Markdown. We simply use a vanilla page template renderer. """
    fileExtension = '.md'

