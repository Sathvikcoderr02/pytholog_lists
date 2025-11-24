import re
from itertools import chain
from more_itertools import unique_everseen

__all__ = ["is_number", "is_variable", "rh_val_get", "unifiable_check", "lh_eval", 
           "list_to_string", "string_to_list", "is_list_like", "list_head_tail", "prob_parser", "rule_terms", "term_checker", "get_path", "pl_read", "answer_handler"] #used in unify module

## a variable is anything that starts with an uppercase letter or is an _
def is_variable(term):
    if not isinstance(term, str) or not term:
        return False
    if is_number(term):
        return False
    # Variable starts with uppercase or underscore
    return term[0].isupper() or term.startswith('_')
    
## check whether there is a number in terms or not        
def is_number(s):
    # Handle non-string inputs (like lists)
    if not isinstance(s, (str, int, float)):
        return False
    try:
        float(s)
        return True
    except (ValueError, TypeError):
        return False        
        
## it parses the operations and returns the keys and the values to be evaluated        
def prob_parser(domain, rule_string, rule_terms):
    if "is" in rule_string:
        s = rule_string.split("is")
        key = s[0]
        value = s[1]
    else:
        key = list(domain.keys())[0]
        value = rule_string
    for i in rule_terms:
        if i in domain.keys():
            value = re.sub(i, str(domain[i]), value)
    value = re.sub(r"(and|or|in|not)", r" \g<0> ", value) ## add spaces after and before the keywords so that eval() can see them
    return key, value
    
def rule_terms(rule_string):  ## getting list of unique terms
    # Handle empty list case
    if '[]' in rule_string and rule_string.strip() == '[]':
        return [[]]
    
    # Handle list patterns like [H|T] or [X|_]
    if '|' in rule_string and rule_string.startswith('[') and rule_string.endswith(']'):
        return [rule_string]
    
    # Handle general case with parentheses
    s = re.sub(r"\s+", "", rule_string)  # Remove all whitespace
    terms = []
    
    # Find all terms inside parentheses
    matches = re.findall(r"\(([^)]+)\)", s)
    if not matches:  # No parentheses found, return the whole string as a single term
        return [s] if s else []
    
    # Split terms by commas, but not inside brackets or quotes
    for match in matches:
        current = ""
        depth = 0
        in_quotes = False
        
        for char in match:
            if char == '"' or char == "'":
                in_quotes = not in_quotes
                current += char
            elif char == '[' and not in_quotes:
                depth += 1
                current += char
            elif char == ']' and not in_quotes:
                depth -= 1
                current += char
            elif char == ',' and depth == 0 and not in_quotes:
                if current:
                    terms.append(current)
                    current = ""
            else:
                current += char
        
        if current:
            terms.append(current)
    
    # Process each term to handle empty lists and other special cases
    result = []
    for term in terms:
        if term == '[]':
            result.append([])
        elif '|' in term and term.startswith('[') and term.endswith(']'):
            # This is a list pattern like [H|T], keep it as is
            result.append(term)
        else:
            result.append(term)
    
    return list(unique_everseen(result))
    
## the function that takes care of equalizing all uppercased variables
def term_checker(expr):
    if not hasattr(expr, 'terms') or not hasattr(expr, 'predicate'):
        return [], str(expr)
        
    terms = []
    for term in expr.terms:
        if isinstance(term, list):
            # Handle list terms by converting them to a string representation
            terms.append('[' + ','.join(str(t) for t in term) + ']')
        else:
            terms.append(str(term))
    
    # Find variable indices (terms starting with uppercase or underscore)
    indx = [i for i, term in enumerate(terms) 
            if isinstance(term, str) and (term[0].isupper() or term.startswith('_'))]
    
    # Create a lookup key for caching
    lookup_terms = terms.copy()
    for i in indx:
        lookup_terms[i] = f"Var{i}"
    
    lookup_key = f"{expr.predicate}({','.join(lookup_terms)})"
    return indx, lookup_key
    
def get_path(db, expr, path):
    terms = db[expr.predicate]["facts"][0].lh.terms
    path = [{k: i[k] for k in i.keys() if k not in terms} for i in path]
    pathe = [] 
    for i in path:
        for k,v in i.items():
            pathe.append(v)
    return set(pathe)

def pl_read(kb, file):
    file = open(file, "r")
    lines = file.readlines()
    facts = []
    for i in lines:
        i = i.strip()
        i = re.sub(r'\.+$', "", i)
        facts.append(i)
    kb(facts)
    print(f"facts and rules have been added to {kb.name}.db")


def rh_val_get(rh_arg, lh_arg, rh_domain):
    if is_variable(rh_arg):
        rh_val = rh_domain.get(rh_arg)
    else: rh_val = rh_arg
    
    return rh_val
    
def unifiable_check(nterms, rh, lh):
    if nterms != len(lh.terms): 
        return False
    if rh.predicate != lh.predicate: 
        return False
    
def lh_eval(rh_val, lh_arg, lh_domain):
    if is_variable(lh_arg):  #variable in destination
        lh_val = lh_domain.get(lh_arg)
        if not lh_val: 
            lh_domain[lh_arg] = rh_val
            #return lh_domain
        elif lh_val != rh_val:
            return False          
    elif lh_arg != rh_val: 
        return False

def list_to_string(lst):
    """Convert a list to its string representation"""
    if not isinstance(lst, (list, tuple)):
        return str(lst)
    return '[' + ', '.join(list_to_string(x) for x in lst) + ']'

def string_to_list(s):
    """Convert a string representation of a list to an actual list"""
    if not isinstance(s, str):
        return s
    try:
        # Handle empty list
        if s == '[]':
            return []
        # Handle list with | (tail) syntax
        if '|' in s:
            head, tail = s.split('|', 1)
            head = head.strip().strip('[]').strip()
            tail = tail.strip()
            head_list = [x.strip() for x in head.split(',')] if head else []
            return head_list + (string_to_list(tail) if tail else [])
        # Handle normal list
        if s.startswith('[') and s.endswith(']'):
            content = s[1:-1].strip()
            if not content:
                return []
            return [x.strip() for x in content.split(',')]
        return s
    except (ValueError, SyntaxError, AttributeError):
        return s

def is_list_like(term):
    """Check if a term is a list or list-like structure"""
    if isinstance(term, str):
        return term.startswith('list(') or term == '[]' or (term.startswith('[') and term.endswith(']'))
    return isinstance(term, (list, tuple))

def list_head_tail(term):
    """Extract head and tail from a list term"""
    if not is_list_like(term):
        return None, None
        
    if term == '[]' or term == []:
        return None, None
    
    if isinstance(term, (list, tuple)):
        if not term:
            return None, None
        if len(term) == 1:
            return term[0], []
        return term[0], term[1:]
    
    # Handle string representation of list
    if isinstance(term, str):
        if term.startswith('list(') and term.endswith(')'):
            content = term[5:-1].split(',', 1)
            if len(content) == 1:
                return content[0].strip(), '[]'
            return content[0].strip(), content[1].strip()
        elif term.startswith('[') and term.endswith(']'):
            content = term[1:-1].strip()
            if not content:
                return None, '[]'
            parts = content.split(',', 1)
            if len(parts) == 1:
                return parts[0].strip(), '[]'
            return parts[0].strip(), '[' + parts[1].strip() + ']'
    
    return None, None

def answer_handler(answer):
    if not answer:
        return ["No"]
    if answer == "No" or answer == "Yes":
        return [answer]
    if isinstance(answer, list):
        if not answer:
            return ["No"]
        # Filter out empty dictionaries and process results
        processed = []
        for item in answer:
            if item == "Yes":
                processed.append(item)
            elif isinstance(item, dict) and item:
                # Convert any list values to proper string representation
                processed_item = {}
                for k, v in item.items():
                    if isinstance(v, list):
                        processed_item[k] = list_to_string(v)
                    else:
                        processed_item[k] = v
                processed.append(processed_item)
        return processed if processed else ["No"]
    return ["No"]

def list_to_string(lst):
    """Convert a list to its string representation"""
    if not isinstance(lst, (list, tuple)):
        return str(lst)
    return '[' + ', '.join(list_to_string(x) for x in lst) + ']'

def string_to_list(s):
    """Convert a string representation of a list to an actual list"""
    if not isinstance(s, str):
        return s
    try:
        # Handle empty list
        if s == '[]':
            return []
        # Handle list with | (tail) syntax
        if '|' in s:
            head, tail = s.split('|', 1)
            head = head.strip().strip('[]').strip()
            tail = tail.strip()
            head_list = [x.strip() for x in head.split(',')] if head else []
            return head_list + (string_to_list(tail) if tail else [])
        # Handle normal list
        if s.startswith('[') and s.endswith(']'):
            content = s[1:-1].strip()
            if not content:
                return []
            return [x.strip() for x in content.split(',')]
        return s
    except (ValueError, SyntaxError, AttributeError):
        return s

def is_list_like(term):
    """Check if a term is a list or list-like structure"""
    if isinstance(term, str):
        return term.startswith('list(') or term == '[]' or (term.startswith('[') and term.endswith(']'))
    return isinstance(term, (list, tuple))

def list_head_tail(term):
    """Extract head and tail from a list term"""
    if not is_list_like(term):
        return None, None
        
    if term == '[]' or term == []:
        return None, None
    
    if isinstance(term, (list, tuple)):
        if not term:
            return None, None
        if len(term) == 1:
            return term[0], []
        return term[0], term[1:]
    
    # Handle string representation of list
    if isinstance(term, str):
        if term.startswith('list(') and term.endswith(')'):
            content = term[5:-1].split(',', 1)
            if len(content) == 1:
                return content[0].strip(), '[]'
            return content[0].strip(), content[1].strip()
        elif term.startswith('[') and term.endswith(']'):
            content = term[1:-1].strip()
            if not content:
                return None, '[]'
            parts = content.split(',', 1)
            if len(parts) == 1:
                return parts[0].strip(), '[]'
            return parts[0].strip(), '[' + parts[1].strip() + ']'
    
    return None, None