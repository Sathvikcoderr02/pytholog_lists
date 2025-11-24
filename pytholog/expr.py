import re

class Expr:
    def __init__ (self, fact):
        self.string = str(fact)  # Initialize string attribute
        self._parse_expr(fact)
            
    def _parse_list(self, term):
        """Parse a list term into its internal representation"""
        print(f"[DEBUG] _parse_list input: {term} (type: {type(term)})")
        
        # If we already have a list pattern, return it as is
        if isinstance(term, list) and len(term) == 3 and term[1] == '|':
            print(f"[DEBUG] Already a list pattern: {term}")
            return term
            
        # Convert to string if not already
        if not isinstance(term, str):
            term_str = str(term).strip()
        else:
            term_str = term.strip()
        
        # Handle empty list
        if not term_str or term_str == '[]':
            print("[DEBUG] Empty list, returning []")
            return []
            
        # Handle list with | (tail) syntax - this is a pattern like [H|T] or [X|_]
        if '|' in term_str and term_str.startswith('[') and term_str.endswith(']'):
            print(f"[DEBUG] Found pattern with | in: {term_str}")
            inner = term_str[1:-1].strip()
            
            # Split on the first | that's not inside nested structures
            depth = 0
            in_quotes = False
            split_pos = -1
            
            for i, c in enumerate(inner):
                if c in ['"', "'"] and (i == 0 or inner[i-1] != '\\'):
                    in_quotes = not in_quotes
                elif not in_quotes:
                    if c == '[':
                        depth += 1
                    elif c == ']':
                        depth -= 1
                    elif c == '|' and depth == 0:
                        split_pos = i
                        break
            
            if split_pos != -1:
                head_part = inner[:split_pos].strip()
                tail_part = inner[split_pos+1:].strip()
                
                print(f"[DEBUG] Split pattern into head: '{head_part}', tail: '{tail_part}'")
                
                # Parse the head part (can be a single term or a list)
                if head_part.startswith('[') and head_part.endswith(']'):
                    head = self._parse_list(head_part[1:-1].strip())
                else:
                    head = self._parse_term(head_part)
                
                # Parse the tail part
                if tail_part == '_':  # Anonymous variable
                    tail = '_'
                elif tail_part[0].isupper() or tail_part.startswith('_'):  # Variable
                    tail = tail_part
                elif tail_part == '[]':  # Empty list
                    tail = []
                elif tail_part.startswith('[') and tail_part.endswith(']'):  # Nested list
                    # Check if it's a pattern like [H|T] in the tail
                    if '|' in tail_part[1:-1]:
                        tail = self._parse_list(tail_part)
                    else:
                        tail = self._parse_list(tail_part[1:-1].strip())
                else:  # Single term
                    tail = self._parse_term(tail_part)
                
                # Return as a special pattern [head, '|', tail]
                result = [head, '|', tail]
                print(f"[DEBUG] Returning list pattern: {result}")
                return result
            
            print("[DEBUG] Could not properly parse pattern, falling back to normal list parsing")
        
        # Handle comma-separated list
        if ',' in term_str:
            print(f"[DEBUG] Comma-separated list: {term_str}")
            items = []
            current = ""
            depth = 0
            in_quotes = False
            
            for c in term_str:
                if c == '"' or c == "'":
                    in_quotes = not in_quotes
                    current += c
                elif c == '[' and not in_quotes:
                    depth += 1
                    current += c
                elif c == ']' and not in_quotes:
                    depth -= 1
                    current += c
                elif c == ',' and depth == 0 and not in_quotes:
                    if current.strip():
                        items.append(self._parse_term(current.strip()))
                    current = ""
                else:
                    current += c
            
            if current.strip():
                items.append(self._parse_term(current.strip()))
            
            print(f"[DEBUG] Parsed comma-separated items: {items}")
            return items
        
        # Single item list
        if term_str.startswith('[') and term_str.endswith(']'):
            inner = term_str[1:-1].strip()
            if not inner:  # Empty list
                return []
            # Recursively parse the inner content
            return self._parse_list(inner)
            
        # Single term
        print(f"[DEBUG] Single term in list: {term_str}")
        term = self._parse_term(term_str)
        return [term] if term is not None else []
    def _parse_term(self, term):
        """Parse a single term, handling variables and constants"""
        term = term.strip()
        
        # Handle empty string
        if not term:
            return term
            
        # Handle variables (start with uppercase or _)
        if term[0].isupper() or term.startswith('_'):
            return term
            
        # Handle list notation
        if term.startswith('[') and term.endswith(']'):
            return self._parse_list(term[1:-1])
            
        # Handle numbers
        try:
            return int(term)
        except ValueError:
            try:
                return float(term)
            except ValueError:
                pass
                
        # Handle boolean values
        if term.lower() == 'true':
            return True
        if term.lower() == 'false':
            return False
            
        # Default case: treat as atom (string)
        return term

    def _parse_expr(self, expr):
        """Parse a Prolog expression into predicate and terms"""
        expr = expr.strip()
        
        # Debug print
        #print(f"Parsing expression: {expr}")
        
        # Handle empty list
        if expr == '[]' or expr == '[]).':
            self.predicate = '[]'
            self.terms = []
            return
            
        # Handle list notation
        if expr.startswith('[') and expr.endswith(']'):
            self.predicate = 'list'
            list_content = expr[1:-1].strip()
            if not list_content:  # Empty list
                self.terms = []
            else:
                self.terms = self._parse_list(list_content)
            return
            
        # Handle normal predicates
        if "(" not in expr: 
            expr = "(" + expr + ")"
            
        pred_ind = expr.index("(")
        self.predicate = expr[:pred_ind].strip()
        
        # Parse terms, handling nested lists and variables
        term_str = expr[pred_ind+1:-1].strip()
        self.terms = self._parse_term_list(term_str)
        
        self.string = expr
        self.index = 0
        
    def _parse_term_list(self, term_str):
        """Parse a comma-separated list of terms, handling nested structures"""
        if not term_str:
            return []
            
        terms = []
        current = ""
        paren_count = 0
        bracket_count = 0
        in_quotes = False
        
        for char in term_str:
            if char == '"' or char == "'":
                in_quotes = not in_quotes
                current += char
            elif not in_quotes:
                if char == '(':
                    paren_count += 1
                elif char == ')':
                    paren_count -= 1
                elif char == '[':
                    bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
                elif char == ',' and paren_count == 0 and bracket_count == 0:
                    terms.append(current.strip())
                    current = ""
                    continue
            current += char
            
        if current:
            terms.append(current.strip())
            
        # Parse each term
        return [self._parse_term(term) for term in terms]
        current_term = ""
        bracket_count = 0
        in_list = False
        
        for char in term_str:
            if char == '[':
                in_list = True
                current_term += char
                bracket_count += 1
            elif char == ']':
                in_list = False
                current_term += char
                bracket_count -= 1
            elif char == ',' and not in_list and bracket_count == 0:
                # Found a term separator outside of any list
                if current_term.strip():
                    # Handle list in term
                    if '[' in current_term and ']' in current_term:
                        list_start = current_term.index('[')
                        list_end = current_term.rindex(']')
                        before = current_term[:list_start]
                        list_content = current_term[list_start:list_end+1]
                        after = current_term[list_end+1:]
                        parsed_list = self._parse_list(list_content[1:-1])
                        current_term = f"{before}list({parsed_list}){after}"
                    self.terms.append(current_term.strip())
                current_term = ""
            else:
                current_term += char
        
        # Add the last term
        if current_term.strip():
            # Handle list in the last term
            if '[' in current_term and ']' in current_term:
                list_start = current_term.index('[')
                list_end = current_term.rindex(']')
                before = current_term[:list_start]
                list_content = current_term[list_start:list_end+1]
                after = current_term[list_end+1:]
                parsed_list = self._parse_list(list_content[1:-1])
                current_term = f"{before}list({parsed_list}){after}"
            self.terms.append(current_term.strip())
        
        self.string = fact
        self.index = 0
    
    ## return string value of the expr in case we need it elsewhere with different type
    def to_string(self):
        return self.string

    def __repr__ (self) :
        return self.string
        
    def __lt__(self, other):
        return self.terms[self.index] < other.terms[other.index]
        

#pl_expr deprecated
class DeprecationHelper(object):
    def __init__(self, new_target):
        self.new_target = new_target

    def _warn(self):
        from warnings import warn
        warn("pl_expr class has been renamed to Expr!")

    def __call__(self, *args, **kwargs):
        self._warn()
        return self.new_target(*args, **kwargs)

    def __getattr__(self, attr):
        self._warn()
        return getattr(self.new_target, attr)

pl_expr = DeprecationHelper(Expr)       