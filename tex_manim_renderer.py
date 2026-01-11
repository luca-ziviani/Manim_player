"""
LaTeX to Manim Renderer
Renders parsed LaTeX elements as Manim animations
"""

from manim import *
from tex_parser import (
    TexParser, ElementType, TextElement, EquationElement, 
    AlignElement, TheoremLikeElement, ProofElement, SectionElement
)
import pickle


class TexToManimScene(Scene):
    """Renders parsed LaTeX elements as animations"""
    
    def __init__(self, latex_filename, **kwargs):
        super().__init__(**kwargs)
        self.latex_filename = latex_filename
        self.parser = TexParser(latex_filename)
        self.elements = []
        
        # Configuration
        self.TEXT_COLOR = WHITE
        self.FRAME_TEXT_WIDTH = 17
        self.FRAME_TEXT_HEIGHT = 9
        self.FRAME_TEXT_ORIGIN = None  # Set in construct()
        
        # State tracking
        self.text_mobjects = VGroup()
        self.pause_times = [0]
        self.current_time = 0
        
        # Get preamble for LaTeX compilation
        self.tex_template = self._get_preamble()
    
    def construct(self):
        """Main construction method"""
        # Parse the document
        self.elements = self.parser.parse()
        
        # Calculate actual text width from LaTeX
        width_ruler = MathTex(
            r"\rule{\textwidth}{0.1pt}",
            tex_template=self.tex_template,
            font_size=36
        )
        self.FRAME_TEXT_WIDTH = width_ruler.width
        self.FRAME_TEXT_ORIGIN = [-self.FRAME_TEXT_WIDTH/2, self.FRAME_TEXT_HEIGHT/2, 0]
        
        print(f"Text frame width: {self.FRAME_TEXT_WIDTH}")
        
        # Render each element
        for element in self.elements:
            self.render_element(element)
        
        # End of document
        self.end_document()
        self.save_times()
    
    def render_element(self, element):
        """Dispatch to appropriate renderer based on element type"""
        
        renderers = {
            ElementType.TEXT: self.render_text,
            ElementType.EQUATION: self.render_equation,
            ElementType.ALIGN: self.render_align,
            ElementType.THEOREM: self.render_theorem,
            ElementType.LEMMA: self.render_lemma,
            ElementType.PROPOSITION: self.render_proposition,
            ElementType.PROOF: self.render_proof,
            ElementType.SECTION: self.render_section,
        }
        
        renderer = renderers.get(element.element_type)
        if renderer:
            renderer(element)
        else:
            print(f"Warning: No renderer for {element.element_type}")
    
    def render_text(self, element: TextElement):
        """Render plain text"""
        text = Tex(
            element.content,
            tex_environment="flushleft",
            tex_template=self.tex_template,
            font_size=36,
            color=self.TEXT_COLOR
        )
        text.set_stroke(color=self.TEXT_COLOR, width=0.05)
        
        text.next_to(self.get_last_position(), DOWN).align_to(self.FRAME_TEXT_ORIGIN, LEFT)
        
        self.play(Write(text))
        self.text_mobjects.add(text)
        self.check_and_scroll(text)
        self.current_time = self.update_time(1)
    
    def render_equation(self, element: EquationElement):
        """Render equation environment"""
        eq = MathTex(
            r"{" + element.content + r"}",
            tex_environment="equation*",
            tex_template=self.tex_template,
            font_size=36,
            color=self.TEXT_COLOR
        )
        eq.set_stroke(color=self.TEXT_COLOR, width=0.05)
        
        # Center the equation
        eq.next_to(self.get_last_position(), DOWN).align_to(self.FRAME_TEXT_ORIGIN, LEFT)
        eq.shift(RIGHT * (self.FRAME_TEXT_WIDTH - eq.width) / 2)
        
        self.play(Write(eq))
        self.text_mobjects.add(eq)
        self.check_and_scroll(eq)
        self.current_time = self.update_time(1)
    
    def render_align(self, element: AlignElement):
        """Render align environment"""
        # Create the full align as a single MathTex
        # Extract each column as a substring to isolate
        substrings_to_isolate = []
        for row in element.rows:
            substrings_to_isolate.extend([col for col in row if col.strip()])
        
        eq = MathTex(
            element.full_content,
            tex_environment="align*",
            tex_template=self.tex_template,
            font_size=36,
            color=self.TEXT_COLOR,
            substrings_to_isolate=substrings_to_isolate
        )
        
        eq.next_to(self.get_last_position(), DOWN).align_to(self.FRAME_TEXT_ORIGIN, LEFT)
        eq.shift(RIGHT * (self.FRAME_TEXT_WIDTH - eq.width) / 2)
        
        # Animate each isolated substring sequentially
        for substring in substrings_to_isolate:
            try:
                eq_part = eq.get_part_by_tex(substring)
                self.play(Write(eq_part))
                self.text_mobjects.add(eq_part)

                # Check if we need to scroll
                if self.get_last_position().get_bottom()[1] - eq_part.height < -self.FRAME_TEXT_HEIGHT/2:
                    # Don't write align too long
                    self.scroll(0.5 * self.FRAME_TEXT_HEIGHT)
                    index_part = eq.submobjects.index(eq_part)
                    eq[index_part+1:].shift(0.5 * self.FRAME_TEXT_HEIGHT * UP)
            except ValueError:
                # Substring not found, skip
                print(f"Warning: Could not find substring in align: {substring[:30]}...")
                continue
        
        self.current_time = self.update_time(len(substrings_to_isolate))
    
    def render_theorem_like(self, element: TheoremLikeElement, color, name):
        """Generic renderer for theorem-like environments"""
        # Create a group for all theorem content
        thm_group = VGroup()
        thm_animations = []
        
        # Theorem header
        if element.label:
            header = Tex(
                rf"\textbf{{{name}}} ({element.label})",
                font_size=40,
                color=color
            )
        else:
            header = Tex(
                rf"\textbf{{{name}}}",
                font_size=40,
                color=color
            )
        
        header.next_to(self.get_last_position(), DOWN).align_on_border([-1, 0, 0], buff=1)
        thm_group.add(header)
        thm_animations.append(Write(header))
        
        # Render theorem content
        for sub_element in element.content:
            if isinstance(sub_element, TextElement):
                text = Tex(
                    sub_element.content,
                    tex_environment="flushleft",
                    tex_template=self.tex_template,
                    font_size=36,
                    color=self.TEXT_COLOR
                )
                text.next_to(thm_group[-1], DOWN).align_to(thm_group[0], LEFT)
                thm_group.add(text)
                thm_animations.append(Write(text))
            
            elif isinstance(sub_element, EquationElement):
                eq = MathTex(
                    r"{" + sub_element.content + r"}",
                    tex_environment="equation*",
                    tex_template=self.tex_template,
                    font_size=36,
                    color=self.TEXT_COLOR
                )
                eq.set_stroke(color=self.TEXT_COLOR, width=0.05)
                eq.next_to(thm_group[-1], DOWN)
                eq.shift(RIGHT * (self.FRAME_TEXT_WIDTH - eq.width) / 2)
                thm_group.add(eq)
                thm_animations.append(Write(eq))
            
            elif isinstance(sub_element, AlignElement):
                # For align inside theorem, render simpler
                eq = MathTex(
                    sub_element.full_content,
                    tex_environment="align*",
                    tex_template=self.tex_template,
                    font_size=36,
                    color=self.TEXT_COLOR
                )
                eq.next_to(thm_group[-1], DOWN).align_to(thm_group[-1], LEFT)
                eq.shift(RIGHT * (self.FRAME_TEXT_WIDTH - eq.width) / 2)
                thm_group.add(eq)
                thm_animations.append(Write(eq))
        
        # Center the whole theorem on screen
        thm_group.move_to(ORIGIN)
        
        # Add surrounding box
        box = SurroundingRectangle(thm_group, color=color, buff=0.3, corner_radius=0.2)
        thm_animations.append(Create(box))
        
        # Clear screen and play
        if self.text_mobjects:
            self.play(FadeOut(*self.text_mobjects))
        
        for anim in thm_animations:
            self.play(anim)
        
        self.wait(1)
        self.play(FadeOut(thm_group, box))
        self.current_time = self.update_time(len(thm_animations))
    
    def render_theorem(self, element: TheoremLikeElement):
        """Render theorem"""
        self.render_theorem_like(element, ORANGE, "Theorem")
    
    def render_lemma(self, element: TheoremLikeElement):
        """Render lemma"""
        self.render_theorem_like(element, GREEN, "Lemma")
    
    def render_proposition(self, element: TheoremLikeElement):
        """Render proposition"""
        self.render_theorem_like(element, BLUE, "Proposition")
    
    def render_proof(self, element: ProofElement):
        """Render proof"""
        prf = Tex(
            r"\textit{Proof.}",
            tex_template=self.tex_template,
            font_size=36,
            color=ORANGE
        )
        prf.next_to(self.get_last_position(), DOWN)
        
        self.play(Write(prf))
        self.text_mobjects.add(prf)
        
        # Render proof content
        for sub_element in element.content:
            self.render_element(sub_element)
        
        self.current_time = self.update_time(1)
    
    def render_section(self, element: SectionElement):
        """Render section header"""
        if self.text_mobjects:
            self.play(FadeOut(*self.text_mobjects))
        
        section_title = Tex(
            element.title,
            color=RED,
            font_size=50
        )
        
        self.play(FadeIn(section_title))
        self.wait(1)
        self.play(FadeOut(section_title))
        self.current_time = self.update_time(2)
    
    # ============== Helper Methods ==============
    
    def get_last_position(self):
        """Get position for next element"""
        if self.text_mobjects:
            return self.text_mobjects[-1]
        else:
            return Dot(self.FRAME_TEXT_ORIGIN)
    
    def check_and_scroll(self, mobject):
        """Check if we need to scroll when adding a mobject"""
        if self.text_mobjects and self.text_mobjects[-1].get_center()[1] < -3.0:
            self.scroll(0.5 * self.FRAME_TEXT_HEIGHT)
    
    def scroll(self, length):
        """Scroll all text upward"""
        self.play(self.text_mobjects.animate.shift(length * UP))
        
        # Remove objects that scrolled off screen
        for mobj in list(self.text_mobjects):
            if mobj.get_bottom()[1] > self.FRAME_TEXT_ORIGIN[1]:
                self.remove(mobj)
                self.text_mobjects.remove(mobj)
    
    def update_time(self, increment):
        """Update timing information"""
        new_time = self.current_time + increment
        self.pause_times.append(new_time)
        return new_time
    
    def end_document(self):
        """Render end of document"""
        if self.text_mobjects:
            self.play(FadeOut(*self.text_mobjects))
        
        thanks = Tex(
            r"Thanks for watching!",
            font_size=100,
            color=self.TEXT_COLOR
        )
        thanks.set_stroke(color=self.TEXT_COLOR, width=0.1)
        
        self.play(Write(thanks))
        self.wait(2)
    
    def save_times(self):
        """Save pause times to file"""
        with open("times.pkl", 'wb') as f:
            pickle.dump(self.pause_times, f)
    
    def _get_preamble(self):
        """Extract preamble from LaTeX file"""
        template = TexTemplate()
        
        try:
            with open(self.latex_filename, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('\\documentclass'):
                        continue
                    if line.startswith('\\begin{document}'):
                        break
                    template.add_to_preamble(line)
        except Exception as e:
            print(f"Warning: Could not read preamble: {e}")
        
        return template


# Example usage
if __name__ == "__main__":
    # To render: manim -pql this_file.py TexToManimScene
    # Or in config: config.scene_names = ["TexToManimScene"]
    pass