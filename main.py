
from tex_manim_renderer import TexToManimScene


class MyPresentation(TexToManimScene):
    def __init__(self, **kwargs):
        super().__init__("SteinWeiss.tex", **kwargs)

# Render with:
# manim -pql main.py MyPresentation