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

config["background_color"] = ManimColor('#150C16')

TEXT_COLOR = ManimColor('#ecfee8')

FRAME_WIDTH = config["frame_width"]
FRAME_HEIGHT = config["frame_height"]

FRAME_TEXT_WIDTH = 10 #FRAME_WIDTH 
FRAME_TEXT_HEIGHT = FRAME_HEIGHT
FRAME_TEXT_ORIGIN = [-5,4.5,0] # point of the frame up left

def update_time(t, increment):
    PAUSE_TIMES.append(t+increment)
    return t + increment

# from "equation.tex %Transformation " write (Transformation( MathTex( equation.tex )))

class LaTex(Scene):
    def construct(self):
        ENV = "" # Can be "equation", "align"
        THM = "" # Can be "theorem", "lemma", "proposition", "proof"
        current_time = 0

        start = Dot(color = BLACK).align_on_border([-1,0,0], buff=1).align_on_border([0,1,0], buff=0.8).shift(UP * 0.5)
        self.add(start)
        
        for line in TEX:
            # Reached bottom of the screen
            if self.mobjects[-1].get_center()[1] < -3.:
                # Cancel and restart from above
                self.play(FadeOut(*self.mobjects))
                self.add(start)
            # Empty tex lines
            if line.startswith("\n"): continue
            
            #   END DOCUMENT
            #---------------------------------------------------------------
            if line.startswith(r"\end{document}"):
                self.play(FadeOut(*self.mobjects))
                thanks = Tex(r"Thanks for watching!", font_size = 100)
                self.play(Write(thanks))
                break
            
            #   SECTION
            #---------------------------------------------------------------
            if line.startswith(r"\section"):
                self.play(FadeOut(*self.mobjects))
                section_title = line.replace(r'\section{', '')
                section_title_tex = Tex( r"{" + section_title, color = RED , font_size = 50)
                self.play(FadeIn(section_title_tex))
                current_time = update_time(current_time, 1)
                self.play(FadeOut(section_title_tex))
                current_time = update_time(current_time, 1)

                print(PAUSE_TIMES)

                self.add(start)
            
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
                THM_animations = []
                THM_group = VGroup()                
                spec = line.replace(r"\begin{thm}","")
                if len(spec)>3:
                    thm = Tex(r"\textbf{Theorem} (" + spec[1:-2] + r")", font_size = 40, color = ORANGE)
                    thm.next_to(self.mobjects[-1], DOWN).align_on_border([-1.,0,0], buff=1)
                else:
                    thm = Tex(r"\textbf{Theorem}", font_size = 40, color = ORANGE)
                    thm.next_to(self.mobjects[-1], DOWN).align_on_border([-1,0,0], buff=1)
                THM_group.add(thm)
                THM_animations.extend([Write(thm)])

            if line.startswith(r"\end{thm}"):
                THM = ""
                THM_group.move_to(ORIGIN)
                THM_box = SurroundingRectangle(THM_group , color = ORANGE, buff=0.3 , corner_radius=0.2)
                THM_animations.extend([Create(THM_box)])

                self.play(FadeOut(*self.mobjects))
                for a in THM_animations:
                    self.play(a)
                self.wait(1)
                self.play(FadeOut(*self.mobjects))
                self.add(start)
                
            #   LEMMA green
            #---------------------------------------------------------------
            if line.startswith(r"\begin{lem}"):
                THM = "lemma"
                THM_animations = []
                THM_group = VGroup()                
                spec = line.replace(r"\begin{lem}","")
                if len(spec)>3:
                    thm = Tex(r"\textbf{Lemma} (" + spec[1:-2] + r")", font_size = 40, color = GREEN)
                    thm.next_to(self.mobjects[-1], DOWN).align_on_border([-1.,0,0], buff=1)
                else:
                    thm = Tex(r"\textbf{Lemma}", font_size = 40, color = GREEN)
                    thm.next_to(self.mobjects[-1], DOWN).align_on_border([-1,0,0], buff=1)
                THM_group.add(thm)
                THM_animations.extend([Write(thm)])

            if line.startswith(r"\end{lem}"):
                THM = ""
                THM_group.move_to(ORIGIN)
                THM_box = SurroundingRectangle(THM_group , color = GREEN, buff=0.3 , corner_radius=0.2)
                THM_animations.extend([Create(THM_box)])

                self.play(FadeOut(*self.mobjects))
                for a in THM_animations:
                    self.play(a)
                self.wait(1)
                self.play(FadeOut(*self.mobjects))
                self.add(start)

            #   PROPOSITION blue
            #---------------------------------------------------------------
            if line.startswith(r"\begin{prop}"):
                THM = "proposition"
                THM_animations = []
                THM_group = VGroup()                
                spec = line.replace(r"\begin{prop}","")
                if len(spec)>3:
                    thm = Tex(r"\textbf{Proposition} (" + spec[1:-2] + r")", font_size = 40, color = BLUE)
                    thm.next_to(self.mobjects[-1], DOWN).align_on_border([-1.,0,0], buff=1)
                else:
                    thm = Tex(r"\textbf{Proposition}", font_size = 40, color = BLUE)
                    thm.next_to(self.mobjects[-1], DOWN).align_on_border([-1,0,0], buff=1)
                THM_group.add(thm)
                THM_animations.extend([Write(thm)])

            if line.startswith(r"\end{prop}"):
                THM = ""
                THM_group.move_to(ORIGIN)
                THM_box = SurroundingRectangle(THM_group , color = BLUE, buff=0.3 , corner_radius=0.2)
                THM_animations.extend([Create(THM_box)])

                self.play(FadeOut(*self.mobjects))
                for a in THM_animations:
                    self.play(a)
                self.wait(1)
                self.play(FadeOut(*self.mobjects))
                self.add(start)
            
            #   EQUATION
            #---------------------------------------------------------------
            if line.startswith(r"\begin{equation") or ENV == "equation":
                if ENV == "":
                    ENV = "equation"
                    continue
                if line.startswith(r"\end{equation"):
                    ENV = ""
                    continue
                if ENV == "equation":
                    eq = MathTex(r"{" + line + r" }" ,tex_environment = "equation*", font_size = 30, color = TEXT_COLOR)
                
                    # If THM on add to a group the equation
                    if THM == "theorem" or THM == "lemma" or THM == "proposition":
                        eq.next_to(THM_group[-1], DOWN)# , aligned_edge = UP)
                        THM_group.add(eq)
                        THM_animations.extend([Write(eq)])
                    else:
                        eq.next_to(self.mobjects[-1], DOWN).align_to(FRAME_TEXT_ORIGIN, LEFT)
                        eq.shift(RIGHT * (FRAME_TEXT_WIDTH - eq.width) /2)
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

            elif line.startswith(r"\begin{align") or ENV =="align":
                if ENV == "":
                    ENV = "align"
                    animations = []
                    list_of_tex = []
                    continue

                if not line.startswith(r"\end{align"):
                    line=line.replace("\\\\", "")
                    line=line.replace("\t&", "")
                    list_of_tex.extend(line.split(r"&"))              
                    continue

                ENV = ""
                group = VGroup()
                N=0
                for formula in list_of_tex:
                    eq = MathTex(formula, font_size = 30, color = TEXT_COLOR)

                    if N==0:
                        eq.next_to(self.mobjects[-1], DOWN).align_on_border([-1.5,0,0], buff=1)
                        animations.extend([FadeIn(eq)])
                        current_time = update_time(current_time, 1)

                        print(PAUSE_TIMES)
                    
                    if N==1:
                            eq.next_to(group[0], RIGHT)
                    
                    if N>1:
                        eq.next_to(group[-1], DOWN, aligned_edge = LEFT)
                    
                    if "%TransformMatchingTex1" in formula: # Transform into the next line
                        previous = group[-1].copy()
                        animations.extend([TransformMatchingTex(previous, eq)])

                    if "%TransformMatchingTex2" in formula: # Transform in the current line
                        eq.next_to(group[-1], RIGHT).align_to(group[-1], LEFT)
                        animations.extend([TransformMatchingTex(group[-1], eq)])
                        group[-1] = eq
                    
                    if "%Add" in formula: 
                        animations.extend([Succession(Wait(0.5),Add(eq),Wait(0.5))])
                        
                    if "%FadeIn" in formula:
                        animations.append(FadeIn(eq))              
                        
                    if "%Write" in formula:
                        animations.extend([Write(eq)])
                    
                    if "%Create" in formula:
                        animations.extend([Create(eq)])
                        
                    if "%DrawBorderThenFill" in formula:
                        animations.extend([DrawBorderThenFill(eq)])
                        
                    if "%GrowFromPoint" in formula:
                        animations.extend([GrowFromPoint(eq, ORIGIN) ])
                        
                    group.add(eq)
                    N+=1
                    
                for a in animations:
                    self.play(a)

                continue

            #   DETECTION TEXT
            #---------------------------------------------------------------
            elif not line.startswith("\\") and not line.startswith("%") and not line.startswith("\t"):                 
                # WARNING: avoid to write lines " \n" instead of "\n" 
                #text = Tex(r"{ \begin{flushleft} " + line + r"\end{flushleft} }", font_size = 30)
                
                if THM == "theorem" or THM == "lemma" or THM == "proposition":
                    text = Tex(r"{ \begin{flushleft} " + line + r"\end{flushleft} }", font_size = 30)
                    text.next_to(THM_group[-1], DOWN)
                    text.align_to(THM_group[0], LEFT)
                    THM_group.add(text)
                    THM_animations.extend([Write(text)])
                else:
                    # tex_environment = None        to have not centered text (default was 'centered')
                    # use \parbox to control the width of text.
                    text = Tex("\\parbox{" + str(FRAME_TEXT_WIDTH)+ "cm}{" + line + "}", tex_environment = None, font_size = 30, color = TEXT_COLOR)
                    text.next_to(self.mobjects[-1], DOWN).align_to(FRAME_TEXT_ORIGIN, LEFT)
                    self.play(Write(text))
                    current_time = update_time(current_time, 1)

                    print(PAUSE_TIMES)
                
            #   MANIM
            #---------------------------------------------------------------
            # If line starts with %Manim, execute a comand in manim
            
            #self.play(FadeOut(*self.mobjects)) # Remove all object with FadeOut

            # Out of the screen:
        with open("times.pkl", 'wb') as file:
            pickle.dump(PAUSE_TIMES, file)
            

# Definitions in the preable

# Add a function to Scroll