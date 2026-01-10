"""
LaTeX to Manim Parser
Parses LaTeX documents into structured elements for animation
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from enum import Enum
import re


class ElementType(Enum):
    TEXT = "text"
    EQUATION = "equation"
    ALIGN = "align"
    THEOREM = "theorem"
    LEMMA = "lemma"
    PROPOSITION = "proposition"
    PROOF = "proof"
    SECTION = "section"


@dataclass
class TexElement:
    """Base class for all LaTeX elements"""
    element_type: ElementType
    line_number: int
    
    
@dataclass
class TextElement(TexElement):
    content: str
    
    def __post_init__(self):
        self.element_type = ElementType.TEXT


@dataclass
class EquationElement(TexElement):
    content: str
    environment: str = "equation"
    
    def __post_init__(self):
        self.element_type = ElementType.EQUATION


@dataclass
class AlignElement(TexElement):
    rows: List[List[str]]  # Each row is a list of column entries
    full_content: str
    
    def __post_init__(self):
        self.element_type = ElementType.ALIGN


@dataclass
class TheoremLikeElement(TexElement):
    """For theorems, lemmas, propositions"""
    theorem_type: ElementType
    label: Optional[str]
    content: List[TexElement]  # Can contain text, equations, etc.
    
    def __post_init__(self):
        self.element_type = self.theorem_type


@dataclass
class ProofElement(TexElement):
    content: List[TexElement]
    
    def __post_init__(self):
        self.element_type = ElementType.PROOF


@dataclass
class SectionElement(TexElement):
    title: str
    
    def __post_init__(self):
        self.element_type = ElementType.SECTION


class ParserState(Enum):
    NORMAL = "normal"
    IN_EQUATION = "in_equation"
    IN_ALIGN = "in_align"
    IN_THEOREM = "in_theorem"
    IN_LEMMA = "in_lemma"
    IN_PROPOSITION = "in_proposition"
    IN_PROOF = "in_proof"


class TexParser:
    """Parses LaTeX documents into structured elements"""
    
    def __init__(self, filename: str):
        self.filename = filename
        self.elements: List[TexElement] = []
        self.state = ParserState.NORMAL
        self.state_stack: List[ParserState] = []
        self.line_number = 0
        
        # Temporary storage for multi-line environments
        self.current_content: List[str] = []
        self.current_theorem_content: List[TexElement] = []
        self.current_align_rows: List[List[str]] = []
        self.current_label: Optional[str] = None
        
        # Regex patterns (compiled once for efficiency)
        self.patterns = {
            'section': re.compile(r'\\section\{(.+)\}'),
            'begin_thm': re.compile(r'\\begin\{thm\}(?:\[(.+)\])?'),
            'begin_lem': re.compile(r'\\begin\{lem\}(?:\[(.+)\])?'),
            'begin_prop': re.compile(r'\\begin\{prop\}(?:\[(.+)\])?'),
            'begin_proof': re.compile(r'\\begin\{proof\}'),
            'begin_equation': re.compile(r'\\begin\{equation\*?\}|\\\['),
            'end_equation': re.compile(r'\\end\{equation\*?\}|\\\]'),
            'begin_align': re.compile(r'\\begin\{align\*?\}'),
            'end_align': re.compile(r'\\end\{align\*?\}'),
            'end_thm': re.compile(r'\\end\{thm\}'),
            'end_lem': re.compile(r'\\end\{lem\}'),
            'end_prop': re.compile(r'\\end\{prop\}'),
            'end_proof': re.compile(r'\\end\{proof\}'),
            'end_document': re.compile(r'\\end\{document\}'),
        }
    
    def parse(self) -> List[TexElement]:
        """Parse the entire LaTeX file and return structured elements"""
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    self.line_number = line_num
                    self._parse_line(line)
            
            return self.elements
        
        except FileNotFoundError:
            raise FileNotFoundError(f"LaTeX file not found: {self.filename}")
        except Exception as e:
            raise Exception(f"Error parsing line {self.line_number}: {str(e)}")
    
    def _parse_line(self, line: str):
        """Parse a single line based on current state"""
        
        # Skip empty lines and pure whitespace
        if line.strip() == '':
            return
        
        # Check for end of document
        if self.patterns['end_document'].search(line):
            return
        
        # Handle different states
        if self.state == ParserState.NORMAL:
            self._parse_normal_line(line)
        elif self.state == ParserState.IN_EQUATION:
            self._parse_equation_line(line)
        elif self.state == ParserState.IN_ALIGN:
            self._parse_align_line(line)
        elif self.state in [ParserState.IN_THEOREM, ParserState.IN_LEMMA, 
                           ParserState.IN_PROPOSITION, ParserState.IN_PROOF]:
            self._parse_theorem_like_line(line)
    
    def _parse_normal_line(self, line: str):
        """Parse line in normal state"""
        
        # Section
        if match := self.patterns['section'].search(line):
            self.elements.append(SectionElement(
                element_type=ElementType.SECTION,
                line_number=self.line_number,
                title=match.group(1)
            ))
            return
        
        # Begin theorem-like environments
        if match := self.patterns['begin_thm'].search(line):
            self._enter_state(ParserState.IN_THEOREM)
            self.current_label = match.group(1) if match.group(1) else None
            return
        
        if match := self.patterns['begin_lem'].search(line):
            self._enter_state(ParserState.IN_LEMMA)
            self.current_label = match.group(1) if match.group(1) else None
            return
        
        if match := self.patterns['begin_prop'].search(line):
            self._enter_state(ParserState.IN_PROPOSITION)
            self.current_label = match.group(1) if match.group(1) else None
            return
        
        if self.patterns['begin_proof'].search(line):
            self._enter_state(ParserState.IN_PROOF)
            return
        
        # Begin equation
        if self.patterns['begin_equation'].search(line):
            self._enter_state(ParserState.IN_EQUATION)
            return
        
        # Begin align
        if self.patterns['begin_align'].search(line):
            self._enter_state(ParserState.IN_ALIGN)
            return
        
        # Regular text (not a command, not a comment)
        if not line.startswith('\\') and not line.startswith('%'):
            self.elements.append(TextElement(
                element_type=ElementType.TEXT,
                line_number=self.line_number,
                content=line.strip()
            ))
    
    def _parse_equation_line(self, line: str):
        """Parse line inside equation environment"""
        if self.patterns['end_equation'].search(line):
            # Create equation element
            self.elements.append(EquationElement(
                element_type=ElementType.EQUATION,
                line_number=self.line_number,
                content=''.join(self.current_content),
                environment='equation'
            ))
            self._exit_state()
        else:
            self.current_content.append(line)
    
    def _parse_align_line(self, line: str):
        """Parse line inside align environment"""
        if self.patterns['end_align'].search(line):
            # Create align element
            self.elements.append(AlignElement(
                element_type=ElementType.ALIGN,
                line_number=self.line_number,
                rows=self.current_align_rows.copy(),
                full_content=''.join(self.current_content)
            ))
            self._exit_state()
        else:
            self.current_content.append(line)
            # Split by & to get columns
            columns = [col.strip() for col in line.split('&')]
            self.current_align_rows.append(columns)
    
    def _parse_theorem_like_line(self, line: str):
        """Parse line inside theorem/lemma/proposition/proof"""
        
        # Check for end of current environment
        end_patterns = {
            ParserState.IN_THEOREM: self.patterns['end_thm'],
            ParserState.IN_LEMMA: self.patterns['end_lem'],
            ParserState.IN_PROPOSITION: self.patterns['end_prop'],
            ParserState.IN_PROOF: self.patterns['end_proof'],
        }
        
        if end_patterns[self.state].search(line):
            # Create appropriate element
            if self.state == ParserState.IN_PROOF:
                self.elements.append(ProofElement(
                    element_type=ElementType.PROOF,
                    line_number=self.line_number,
                    content=self.current_theorem_content.copy()
                ))
            else:
                theorem_type_map = {
                    ParserState.IN_THEOREM: ElementType.THEOREM,
                    ParserState.IN_LEMMA: ElementType.LEMMA,
                    ParserState.IN_PROPOSITION: ElementType.PROPOSITION,
                }
                
                self.elements.append(TheoremLikeElement(
                    element_type=theorem_type_map[self.state],
                    line_number=self.line_number,
                    theorem_type=theorem_type_map[self.state],
                    label=self.current_label,
                    content=self.current_theorem_content.copy()
                ))
            
            self._exit_state()
            return
        
        # Otherwise, recursively parse the content
        # Save current state
        saved_state = self.state
        self.state = ParserState.NORMAL
        
        # Parse the line
        self._parse_line(line)
        
        # If a new element was added, move it to theorem content
        if self.elements and self.elements[-1].line_number == self.line_number:
            self.current_theorem_content.append(self.elements.pop())
        
        # Restore state
        self.state = saved_state
    
    def _enter_state(self, new_state: ParserState):
        """Enter a new parsing state"""
        self.state_stack.append(self.state)
        self.state = new_state
        self.current_content = []
        if new_state in [ParserState.IN_THEOREM, ParserState.IN_LEMMA, 
                        ParserState.IN_PROPOSITION, ParserState.IN_PROOF]:
            self.current_theorem_content = []
        if new_state == ParserState.IN_ALIGN:
            self.current_align_rows = []
    
    def _exit_state(self):
        """Exit current state and return to previous"""
        if self.state_stack:
            self.state = self.state_stack.pop()
        else:
            self.state = ParserState.NORMAL
        
        self.current_content = []
        self.current_label = None


# Example usage
if __name__ == "__main__":
    parser = TexParser("SteinWeiss.tex")
    elements = parser.parse()
    
    # Print parsed structure
    for elem in elements:
        print(f"{elem.element_type.value}: Line {elem.line_number}")
        if isinstance(elem, TextElement):
            print(f"  Content: {elem.content[:50]}...")
        elif isinstance(elem, TheoremLikeElement):
            print(f"  Label: {elem.label}")
            print(f"  Contains {len(elem.content)} sub-elements")