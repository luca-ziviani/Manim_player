# Manim_player

Produce a video with manim automatically from a .tex file.

## Method

1) Write a file my_file.tex as you do to produce a PDF.
2) Modify the main.py file with the name of your file (my_file.tex)
3) Execute the rendering with Manim using: 
   manim -pql main.py MyPresentation 


## How it works

1) tex_parser.py will parse my_file.py to understand the structure (preamble, theorem, ...)
2) tex_manim_renderer.py will explore the parsing and render each element.

## Perspective

In read.py there is a controller in OpenCV to show animations partially like a 
presentation with slides. Need to implement the tracking of time checkpoints 
to allow the video to jump to the correct points.
