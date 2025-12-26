# -*- coding: utf-8 -*-
"""
Created on Fri Jun 20 19:49:40 2025

@author: lucaz
"""

from manim import *
import os
import re
import pickle



FILE_NAME = "main.tex"

os.chdir(os.getcwd())

TEX = open(FILE_NAME, "r")

PAUSE_TIMES = [0]

#--------------- Config ----------------------
# See all attributes at "\manim\_config\default.cfg"

#config["background_color"] = ManimColor('#150C16')
config["background_color"] = BLACK

#TEXT_COLOR = ManimColor('#ecfee8')
TEXT_COLOR = WHITE

FRAME_WIDTH = config["frame_width"]
FRAME_HEIGHT = config["frame_height"]

#FRAME_TEXT_WIDTH = FRAME_WIDTH 
#print(FRAME_TEXT_WIDTH)
FRAME_TEXT_HEIGHT = FRAME_HEIGHT
FRAME_TEXT_ORIGIN = [-7.5,4.5,0] # point of the frame up left

def update_time(t, increment):
    PAUSE_TIMES.append(t+increment)
    return t + increment

# from "equation.tex %Transformation " write (Transformation( MathTex( equation.tex )))

class LaTex(Scene):
    def construct(self):
        ENV = "" # Can be "equation", "align"
        THM = "" # Can be "theorem", "lemma", "proposition", "proof"
        current_time = 0

        # Compute the width of \textwidth in ManimUnits:
        my_template = get_preamble(FILE_NAME)
        print("--------------BEGIN placeholder_text---------------")
        print(my_template.tex_compiler)
        print("--------------END placeholder_text---------------")


        FRAME_TEXT_WIDTH = Tex(r"\rule{\textwidth}{0.1pt}").width
        print(FRAME_TEXT_WIDTH )

        self.start = Dot(color = WHITE).align_on_border([-1,0,0], buff=1).align_on_border([0,1,0], buff=0.8).shift(UP * 0.5)
        self.add(self.start)
        
        for line in TEX:
            # Reached bottom of the screen
            if self.mobjects[-1].get_center()[1] < -3.:
                # Cancel and restart from above
                self.play(FadeOut(*self.mobjects))
                self.add(self.start)
            # Empty tex lines
            if line.startswith("\n"): continue
            
            #   END DOCUMENT
            #---------------------------------------------------------------
            if line.startswith(r"\end{document}"):
                self.EndDocument()
                break
            
            #   SECTION
            #---------------------------------------------------------------
            if line.startswith(r"\section"):
                self.StartSection(line)
                
            
            #   BEGIN PROOF
            #---------------------------------------------------------------
            if line.startswith(r"\begin{proof}"):
                #self.play(FadeOut(*self.mobjects))
                prf = Tex(r"\textit{Proof.}", font_size = 30, color = ORANGE)
                prf.next_to(self.mobjects[-1], DOWN).align_on_border([-1,0,0], buff=1)
                self.play(Write(prf))
            
            #   THEOREM (orange)
            #---------------------------------------------------------------
            if line.startswith(r"\begin{thm}"):
                THM = "theorem"
                self.THM_animations = []
                self.THM_group = VGroup()                
                self.StartTheorem(line)

            if line.startswith(r"\end{thm}"):
                THM = ""
                self.PlayTheorem()
                
                
            #   LEMMA green
            #---------------------------------------------------------------
            if line.startswith(r"\begin{lem}"):
                THM = "lemma"
                self.THM_animations = []
                self.THM_group = VGroup()                
                self.StartLemma(line)

            if line.startswith(r"\end{lem}"):
                THM = ""
                self.PlayLemma()


            #   PROPOSITION blue
            #---------------------------------------------------------------
            if line.startswith(r"\begin{prop}"):
                THM = "proposition"
                self.THM_animations = []
                self.THM_group = VGroup()                
                self.StartProposition(line)

            if line.startswith(r"\end{prop}"):
                THM = ""
                self.PlayProposition()


            #   EQUATION
            #---------------------------------------------------------------
            if line.startswith(r"\begin{equation") or line.startswith(r"\[") or ENV == "equation":
                if ENV == "":
                    ENV = "equation"
                    continue
                if line.startswith(r"\end{equation") or line.startswith(r"\]"):
                    ENV = ""
                    continue
                if ENV == "equation":
                    eq = MathTex(r"{" + line + r" }" ,tex_environment = "equation*", tex_template=my_template, font_size = 30, color = TEXT_COLOR)
                    eq.set_stroke( color=TEXT_COLOR, width=0.05 )

                    # If THM on add to a group the equation
                    if THM == "theorem" or THM == "lemma" or THM == "proposition":
                        eq.next_to(self.THM_group[-1], DOWN)# , aligned_edge = UP)
                        self.THM_group.add(eq)
                        self.THM_animations.extend([Write(eq)])
                    else:
                        eq.next_to(self.mobjects[-1], DOWN).align_to(FRAME_TEXT_ORIGIN, LEFT)
                        eq.shift(RIGHT * (FRAME_TEXT_WIDTH - eq.width) /4)
                        self.play(Write(eq))
                    
                        current_time = update_time(current_time, 1)
                        print(PAUSE_TIMES)
                    

            #   ALIGN
            #---------------------------------------------------------------
            # Split the line as latex: create columns of equations according to &
            # - Set a default animation for each entry
            # - define \newcommand{\FadeIn}{} in the .tex file, but without effect
            #   so the pdf will not be modified and i have bookmarks for animations
            # - If i see \FadeIn in formula, do a FadeIn animation for that formula
            # [[[row[i], row[i+1]] for i in range(0,len(row),2) ] for row in lista]
            #
            # 1) create  [ [[f1, f2], [f3, f4]],
            #              [[f5, f6], [f7, f8]] ]
            #              
            # 2) align vertically f2, f6 and f4, f8
            #
            # 3) compute len of f1 as MathTex object, the next index in f1.join(f2) will be '&'
            #
            # 4) use get_part_by_tex() to obtain a subformula of the whole align.

            elif line.startswith(r"\begin{align") or ENV == "align":
                if ENV == "":
                    ENV = "align"
                    self.len_sub_formulas = []
                    self.Total_align = ""
                    self.Align_Matrix = []
                    self.Align_Group = VGroup()  
                    self.Align_Animations = []
                    continue
                if line.startswith(r"\end{align"):
                    ENV = ""
                    print("FINAL MATRIX:")
                    print(self.Align_Matrix)
                    eq = MathTex(self.Total_align, tex_environment = "align*", tex_template=my_template, font_size = 30, color = TEXT_COLOR)
                    eq.next_to(self.mobjects[-1], DOWN).align_to(FRAME_TEXT_ORIGIN, LEFT)
                    self.play(Write(eq))

                    # Untill here I can write the whole align thanks to the string Total_align
                    # and I kept track of the structure of the align. Now I need to build the 
                    # sub-Mobjects of the equation and define the transformations. 
                    # Fill the list Align_Animations


                    continue
                    # Play the animations
                    if THM == "theorem" or THM == "lemma" or THM == "proposition":
                        eq.next_to(self.THM_group[-1], DOWN).align_to(FRAME_TEXT_ORIGIN, LEFT)
                        eq.shift(RIGHT * (FRAME_TEXT_WIDTH - eq.width) /4)
                        self.THM_group.add(*self.Align_Group) 
                        self.THM_animations.extend(*self.Align_Animations)
                    else:
                        eq.next_to(self.mobjects[-1], DOWN).align_to(FRAME_TEXT_ORIGIN, LEFT)
                        eq.shift(RIGHT * (FRAME_TEXT_WIDTH - eq.width) /4)

                        i=0
                        for len_sub_formula in self.len_sub_formulas:
                            self.play(Write(eq[0][i:i+len_sub_formula]))
                            self.wait(1)
                            i+=len_sub_formula
                    continue
                if ENV == "align":
                    self.Total_align += line
                    if "\\\\" in line:
                        line = line.replace("\\\\", "")
                    if line.startswith("\t"):
                        line = line.replace("\t", "")
                    
                    # ADD HERE GET_INFO ABOUT TRANSFORM, FADE,...

                    row = line.split('&')
                    print(row)

                    self.Align_Matrix.append( [[row[i], row[i+1]] for i in range(0,len(row),2) ] )
                    #self.Align_Matrix.append( [ row[i] + row[i+1] for i in range(0,len(row),2) ] )
                    

                    continue

                    eq = MathTex(line ,tex_environment = "align*", tex_template=my_template, font_size = 30, color = TEXT_COLOR)
                    eq.set_stroke( color=TEXT_COLOR, width=0.05 )
                    
                    tex_list = line.split('&')  # this is when stop the animation, maybe change '&' to another comand
                                                # However, it has to be an invisible character!

                    for tex in tex_list:
                        print(tex)
                        if "\\\\" in tex:
                            tex = tex.replace("\\\\", "")
                        if tex.startswith("\t"):
                            tex = tex.replace("\t", "")
                        # Compute the lenght of each subformula
                        formula = MathTex(tex, tex_template=my_template)
                        if isinstance(formula, list) and len(formula)>0:
                            self.len_sub_formulas.append(len(formula[0]))
                        

                    

                    
                        
            
            #   DETECTION TEXT
            #---------------------------------------------------------------
            elif not line.startswith("\\") and not line.startswith("%") and not line.startswith("\t"):                 
                # WARNING: avoid to write lines " \n" instead of "\n" 
                #text = Tex(r"{ \begin{flushleft} " + line + r"\end{flushleft} }", font_size = 30)
                
                if THM == "theorem" or THM == "lemma" or THM == "proposition":
                    text = Tex(r"{ \begin{flushleft} " + line + r"\end{flushleft} }", font_size = 30)
                    text.next_to(self.THM_group[-1], DOWN)
                    text.align_to(self.THM_group[0], LEFT)
                    self.THM_group.add(text)
                    self.THM_animations.extend([Write(text)])
                else:
                    # tex_environment = None        to have not centered text (default was 'centered')
                    # use \parbox to control the width of text. 
                    # WARNING: here FRAME_TEXT_WIDTH is used in cm, not with units of the manim frame
                    text = Tex(line,tex_environment = "flushleft", tex_template=my_template,  font_size = 30, color = TEXT_COLOR)
                    text.set_stroke( color=TEXT_COLOR, width=0.05 )
                    text.next_to(self.mobjects[-1], DOWN).align_to(FRAME_TEXT_ORIGIN, LEFT)
                    self.play(Write(text))
                    current_time = update_time(current_time, 1)

                    print(PAUSE_TIMES)
                
            #   MANIM
            #---------------------------------------------------------------
            # If line starts with %Manim, execute a comand in manim
            
            #self.play(FadeOut(*self.mobjects)) # Remove all object with FadeOut

            # Out of the screen:
        self.SaveTimes()

    def EndDocument(self):
        self.play(FadeOut(*self.mobjects))
        thanks = Tex(r"Thanks for watching!", font_size = 100, color = TEXT_COLOR)
        thanks.set_stroke( color=TEXT_COLOR, width=0.1 )
        self.play(Write(thanks))
        return

    def StartSection(self,line):
        self.play(FadeOut(*self.mobjects))
        section_title = line.replace(r'\section{', '')
        section_title_tex = Tex( r"{" + section_title, color = RED , font_size = 50)
        self.play(FadeIn(section_title_tex))
        self.play(FadeOut(section_title_tex))
        self.add(self.start)
        return

    def StartTheorem(self,line):
        specification = line.replace(r"\begin{thm}","")
        if len(specification)>3:
            thm = Tex(r"\textbf{Theorem} (" + specification[1:-2] + r")", font_size = 40, color = ORANGE)
            thm.next_to(self.mobjects[-1], DOWN).align_on_border([-1.,0,0], buff=1)
        else:
            thm = Tex(r"\textbf{Theorem}", font_size = 40, color = ORANGE)
            thm.next_to(self.mobjects[-1], DOWN).align_on_border([-1,0,0], buff=1)
        self.THM_group.add(thm)
        self.THM_animations.extend([Write(thm)])
        return

    def StartLemma(self,lemma):
        spec = line.replace(r"\begin{lem}","")
        if len(spec)>3:
            thm = Tex(r"\textbf{Lemma} (" + spec[1:-2] + r")", font_size = 40, color = GREEN)
            thm.next_to(self.mobjects[-1], DOWN).align_on_border([-1.,0,0], buff=1)
        else:
            thm = Tex(r"\textbf{Lemma}", font_size = 40, color = GREEN)
            thm.next_to(self.mobjects[-1], DOWN).align_on_border([-1,0,0], buff=1)
        self.THM_group.add(thm)
        self.THM_animations.extend([Write(thm)])
        return

    def StartProposition(self,line):
        spec = line.replace(r"\begin{prop}","")
        if len(spec)>3:
            thm = Tex(r"\textbf{Proposition} (" + spec[1:-2] + r")", font_size = 40, color = BLUE)
            thm.next_to(self.mobjects[-1], DOWN).align_on_border([-1.,0,0], buff=1)
        else:
            thm = Tex(r"\textbf{Proposition}", font_size = 40, color = BLUE)
            thm.next_to(self.mobjects[-1], DOWN).align_on_border([-1,0,0], buff=1)
        self.THM_group.add(thm)
        self.THM_animations.extend([Write(thm)])
        return


    def PlayTheorem(self):
        self.THM_group.move_to(ORIGIN)
        THM_box = SurroundingRectangle(self.THM_group , color = ORANGE, buff=0.3 , corner_radius=0.2)
        self.THM_animations.extend([Create(THM_box)])
        self.play(FadeOut(*self.mobjects))
        for anim in self.THM_animations:
            self.play(anim)
        self.wait(1)
        self.play(FadeOut(*self.mobjects))
        self.add(self.start)
        return

    def PlayLemma(self):
        self.THM_group.move_to(ORIGIN)
        THM_box = SurroundingRectangle(self.THM_group , color = GREEN, buff=0.3 , corner_radius=0.2)
        self.THM_animations.extend([Create(THM_box)])
        self.play(FadeOut(*self.mobjects))
        for anim in self.THM_animations:
            self.play(anim)
        self.wait(1)
        self.play(FadeOut(*self.mobjects))
        self.add(self.start)
        return

    def PlayProposition(self):
        self.THM_group.move_to(ORIGIN)
        THM_box = SurroundingRectangle(self.THM_group , color = BLUE, buff=0.3 , corner_radius=0.2)
        self.THM_animations.extend([Create(THM_box)])
        self.play(FadeOut(*self.mobjects))
        for a in self.THM_animations:
            self.play(a)
        self.wait(1)
        self.play(FadeOut(*self.mobjects))
        self.add(self.start)
        return    

    def SaveTimes(self):
        """
        Save times in a .pkl file
        """
        with open("times.pkl", 'wb') as file:
            pickle.dump(PAUSE_TIMES, file)
        return

    def Scroll(self):
        """
        Scroll all self.mobjects upward if the end of the screen is reached 
        """
        pass

    def ResizeText(self):
        """
        Resize and move the text to somewhere else. Maybe to give space to show a figure
        """
        pass


# Add a function to Scroll
def get_preamble(name_file):
    # TODO: Security check: avoid {{ }} in the preamble
    my_template = TexTemplate()
    with open(name_file, "r") as file_tex:
        for line in file_tex:
            if line.startswith('\\documentclass'):
                continue
            if line.startswith('\\begin{document}'):
                break
            my_template.add_to_preamble(line)
    return my_template


