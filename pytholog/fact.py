from .util import rule_terms
import re
from .expr import Expr

class Fact:
    def __init__ (self, fact):
        self._parse_fact(fact)
        
    def _parse_fact(self, fact):
        # Preserve the original fact for debugging
        original_fact = fact
        
        # Special handling for empty list facts
        if fact.strip() == 'empty_list([]).':
            self.lh = Expr('empty_list([])')
            self.rhs = []
            self.fact = 'empty_list([]).'
            return
        
        # Remove all whitespace except inside string literals
        in_quotes = False
        clean_fact = []
        for c in fact:
            if c == '"':
                in_quotes = not in_quotes
                clean_fact.append(c)
            elif c.isspace() and not in_quotes:
                continue
            else:
                clean_fact.append(c)
        fact = ''.join(clean_fact)
        
        # Parse the fact
        self.terms = rule_terms(fact)
        
        if ":-" in fact: 
            if_ind = fact.index(":-")
            self.lh = Expr(fact[:if_ind])
            
            # Handle the right-hand side of the rule
            rhs_str = fact[if_ind + 2:]
            
            # Split on commas that are not inside lists or other nested structures
            rhs_parts = []
            current = ""
            depth = 0
            in_list = False
            
            for c in rhs_str:
                if c == '[':
                    in_list = True
                    depth += 1
                elif c == ']':
                    depth -= 1
                    if depth == 0:
                        in_list = False
                elif c == ',' and not in_list and depth == 0:
                    if current:
                        rhs_parts.append(current)
                        current = ""
                    continue
                
                current += c
            
            if current:
                rhs_parts.append(current)
            
            # Parse each part of the right-hand side
            self.rhs = []
            for part in rhs_parts:
                # Remove trailing period if present
                if part.endswith('.'):
                    part = part[:-1]
                self.rhs.append(Expr(part))
            
            # Reconstruct the fact string
            rs = [g.to_string() for g in self.rhs]
            self.fact = f"{self.lh.to_string()}:-{','.join(rs)}."
        else:   
            # Remove trailing period if present
            if fact.endswith('.'):
                fact = fact[:-1]
            
            self.lh = Expr(fact)
            self.rhs = []
            self.fact = f"{self.lh.to_string()}."  # Add back the period
    
    ## returning string value of the fact
    def to_string(self):
        return self.fact

    def __repr__ (self) :
        return self.fact
        
    def __lt__(self, other):
        self_term = self.lh.terms[self.lh.index]
        other_term = other.lh.terms[other.lh.index]
        
        # Convert list to string for comparison if needed
        if isinstance(self_term, list):
            self_term = str(self_term)
        if isinstance(other_term, list):
            other_term = str(other_term)
            
        return self_term < other_term
        