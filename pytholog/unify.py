from .util import *
import re
from .expr import Expr
from .expr import Expr
from .fact import Fact

def is_list_term(term):
    """Check if a term represents a list"""
    if term == [] or term == '[]':
        return True
    if isinstance(term, str):
        return term.startswith('list(') or term == '[]' or \
               (term.startswith('[') and term.endswith(']'))
    if hasattr(term, 'predicate'):
        return term.predicate in ['list', '[]']
    if hasattr(term, 'terms') and term.predicate == '[]':
        return True
    return isinstance(term, list)

def unify_lists(lh_list, rh_list, lh_domain, rh_domain):
    """Unify two list terms, handling patterns like [H|T] and [_|_]"""
    print(f"\n[DEBUG] unify_lists: {lh_list} with {rh_list}")
    print(f"lh_domain: {lh_domain}")
    print(f"rh_domain: {rh_domain}")
    
    # Helper function to check if a term is a list pattern like [H|T]
    def is_list_pattern(term):
        if isinstance(term, list) and len(term) == 3 and term[1] == '|':
            return True
        if isinstance(term, str) and '|' in term and term.startswith('[') and term.endswith(']'):
            return True
        return False
    
    # Helper function to parse list pattern [H|T] into (head, tail)
    def parse_list_pattern(pattern):
        # If it's already in parsed form [head, '|', tail]
        if isinstance(pattern, list) and len(pattern) == 3 and pattern[1] == '|':
            return pattern[0], pattern[2]
            
        # If it's a string like "[H|T]"
        if isinstance(pattern, str) and '|' in pattern and pattern.startswith('[') and pattern.endswith(']'):
            inner = pattern[1:-1].strip()
            # Handle cases like "[H|T]" or "[H | T]"
            if '|' in inner:
                head, tail = inner.split('|', 1)
                return head.strip(), tail.strip()
        
        # If it's a list with a single string like ['H|T']
        if isinstance(pattern, list) and len(pattern) == 1 and '|' in pattern[0]:
            inner = pattern[0].strip('[] ')
            if '|' in inner:
                head, tail = inner.split('|', 1)
                return head.strip(), tail.strip()
                
        return None, None
    
    # Handle empty lists
    if (lh_list == [] or lh_list == '[]') and (rh_list == [] or rh_list == '[]'):
        print("[DEBUG] Both lists are empty, returning True")
        return True
    
    # Handle case where one side is empty and the other is not
    if (lh_list == [] or lh_list == '[]') or (rh_list == [] or rh_list == '[]'):
        # Check if the non-empty side is a variable that can be bound to an empty list
        if (isinstance(lh_list, str) and (lh_list[0].isupper() or lh_list.startswith('_')) and 
            (rh_list == [] or rh_list == '[]')):
            print(f"[DEBUG] Binding LHS variable {lh_list} to empty list")
            lh_domain[lh_list] = []
            return True
        elif (isinstance(rh_list, str) and (rh_list[0].isupper() or rh_list.startswith('_')) and 
              (lh_list == [] or lh_list == '[]')):
            print(f"[DEBUG] Binding RHS variable {rh_list} to empty list")
            rh_domain[rh_list] = []
            return True
        print("[DEBUG] One list is empty and the other is not, returning False")
        return False
    
    # Check if either side is a list pattern
    lh_head, lh_tail = parse_list_pattern(lh_list)
    rh_head, rh_tail = parse_list_pattern(rh_list)
    
    # Debug print for list patterns
    if lh_head is not None:
        print(f"[DEBUG] LHS list pattern: {lh_head} | {lh_tail}")
    if rh_head is not None:
        print(f"[DEBUG] RHS list pattern: {rh_head} | {rh_tail}")
    
    # Case 1: Both sides are list patterns
    if lh_head is not None and rh_head is not None:
        print("[DEBUG] Both sides are list patterns, unifying heads and tails")
        
        # Make copies of the domains to avoid polluting them
        lh_domain_copy = lh_domain.copy()
        rh_domain_copy = rh_domain.copy()
        
        # Unify heads
        if not unify_terms(lh_head, rh_head, lh_domain_copy, rh_domain_copy):
            print("[DEBUG] Head unification failed")
            return False
            
        # If either tail is an anonymous variable, it matches anything
        if lh_tail == '_' or rh_tail == '_':
            print("[DEBUG] Anonymous variable in tail, matching anything")
            lh_domain.update(lh_domain_copy)
            rh_domain.update(rh_domain_copy)
            return True
            
        # Unify tails
        if not unify_terms(lh_tail, rh_tail, lh_domain_copy, rh_domain_copy):
            print("[DEBUG] Tail unification failed")
            return False
            
        # If we got here, unification succeeded - update the original domains
        lh_domain.update(lh_domain_copy)
        rh_domain.update(rh_domain_copy)
        return True
        
    # Case 2: One side is a list pattern and the other is a concrete list
    if lh_head is not None and isinstance(rh_list, list):
        print("[DEBUG] LHS is a list pattern, RHS is a concrete list")
        if not rh_list:  # If RHS is empty, only match if LHS is also empty
            return lh_head == [] and lh_tail == []
            
        # Unify head with first element
        if not unify_terms(lh_head, rh_list[0], lh_domain, rh_domain):
            return False
            
        # If tail is an anonymous variable, it matches anything
        if lh_tail == '_':
            return True
            
        # Recursively unify the tail with the rest of the list
        return unify_terms(lh_tail, rh_list[1:], lh_domain, rh_domain)
        
    if rh_head is not None and isinstance(lh_list, list):
        print("[DEBUG] RHS is a list pattern, LHS is a concrete list")
        if not lh_list:  # If LHS is empty, only match if RHS is also empty
            return rh_head == [] and rh_tail == []
            
        # Unify head with first element
        if not unify_terms(rh_head, lh_list[0], rh_domain, lh_domain):
            return False
            
        # If tail is an anonymous variable, it matches anything
        if rh_tail == '_':
            return True
            
        # Recursively unify the tail with the rest of the list
        return unify_terms(rh_tail, lh_list[1:], rh_domain, lh_domain)
            
        # If we get here, head unification succeeded, update the domains
        lh_domain.update(lh_domain_copy)
        rh_domain.update(rh_domain_copy)
        
        # Handle tails
        # If either tail is an anonymous variable, it matches anything
        if lh_tail == '_' or rh_tail == '_':
            print("[DEBUG] Anonymous variable in tail, matching anything")
            return True
            
        # If both tails are empty lists, we're done
        if (lh_tail == '[]' or lh_tail == []) and (rh_tail == '[]' or rh_tail == []):
            print("[DEBUG] Both tails are empty")
            return True
            
        # If one tail is empty and the other is not, they don't unify
        if (lh_tail == '[]' or lh_tail == []) or (rh_tail == '[]' or rh_tail == []):
            print("[DEBUG] One tail is empty, the other is not")
            return False
            
        # Recurse on the tails
        print(f"[DEBUG] Recursing on tails: {lh_tail} and {rh_tail}")
        return unify_terms(lh_tail, rh_tail, lh_domain, rh_domain)
    
    # Case 2: Left is a list pattern, right is a concrete list
    elif lh_head is not None and isinstance(rh_list, list):
        print(f"[DEBUG] LHS is a list pattern, RHS is a concrete list")
        
        # If the right list is empty, the tail must also be empty
        if not rh_list:
            print("[DEBUG] RHS is empty list")
            return lh_tail == '[]' or lh_tail == []
            
        # Unify the head of the pattern with the first element of the list
        print(f"[DEBUG] Unifying head {lh_head} with {rh_list[0]}")
        
        # Make copies of the domains to avoid polluting them
        lh_domain_copy = lh_domain.copy()
        rh_domain_copy = rh_domain.copy()
        
        if not unify_terms(lh_head, rh_list[0], lh_domain_copy, rh_domain_copy):
            print("[DEBUG] Head unification failed")
            return False
            
        # If we get here, head unification succeeded, update the domains
        lh_domain.update(lh_domain_copy)
        rh_domain.update(rh_domain_copy)
        
        # Handle the tail
        if lh_tail == '_':  # Anonymous variable, match anything
            print("[DEBUG] Anonymous variable in tail, matching rest of list")
            return True
            
        if lh_tail == '[]' or lh_tail == []:  # Empty tail, so list should have exactly one element
            result = len(rh_list) == 1
            print(f"[DEBUG] Empty tail, checking if list has exactly one element: {result}")
            return result
            
        # Handle variable tail (e.g., [H|T] where T is a variable)
        if isinstance(lh_tail, str) and (lh_tail[0].isupper() or lh_tail.startswith('_')):
            print(f"[DEBUG] Tail is a variable: {lh_tail}")
            if lh_tail in lh_domain:
                print(f"[DEBUG] Tail variable {lh_tail} is already bound to {lh_domain[lh_tail]}")
                return unify_lists(lh_domain[lh_tail], rh_list[1:], lh_domain, rh_domain)
            else:
                print(f"[DEBUG] Binding tail variable {lh_tail} to {rh_list[1:]}")
                lh_domain[lh_tail] = rh_list[1:]
                return True
        
        # Recurse with the tail
        print(f"[DEBUG] Recursing with tail: {lh_tail} and {rh_list[1:]}")
        return unify_lists(lh_tail, rh_list[1:], lh_domain, rh_domain)
    
    # Case 3: Right is a list pattern, left is a concrete list
    elif rh_head is not None and isinstance(lh_list, list):
        print("[DEBUG] RHS is a list pattern, LHS is a concrete list, swapping")
        return unify_lists(rh_list, lh_list, rh_domain, lh_domain)  # Swap and retry
    
    # Case 4: Both are regular lists, unify element by element
    elif isinstance(lh_list, list) and isinstance(rh_list, list):
        if len(lh_list) != len(rh_list):
            print(f"[DEBUG] Lists have different lengths: {len(lh_list)} vs {len(rh_list)}")
            return False
            
        print(f"[DEBUG] Unifying lists element by element: {lh_list} and {rh_list}")
        
        # Make a copy of the domains to avoid polluting them
        lh_domain_copy = lh_domain.copy()
        rh_domain_copy = rh_domain.copy()
        
        for lh_item, rh_item in zip(lh_list, rh_list):
            if not unify_terms(lh_item, rh_item, lh_domain_copy, rh_domain_copy):
                print("[DEBUG] List element unification failed")
                return False
        
        # If we get here, all elements unified successfully, update the domains
        lh_domain.update(lh_domain_copy)
        rh_domain.update(rh_domain_copy)
        return True
    
    # Case 5: One side is a variable, the other is a list
    elif isinstance(lh_list, str) and (lh_list[0].isupper() or lh_list.startswith('_')):
        print(f"[DEBUG] LHS is a variable: {lh_list}")
        if lh_list in lh_domain:
            print(f"[DEBUG] LHS variable {lh_list} is already bound to {lh_domain[lh_list]}")
            return unify_lists(lh_domain[lh_list], rh_list, lh_domain, rh_domain)
        else:
            print(f"[DEBUG] Binding LHS variable {lh_list} to {rh_list}")
            lh_domain[lh_list] = rh_list
            return True
            
    elif isinstance(rh_list, str) and (rh_list[0].isupper() or rh_list.startswith('_')):
        print(f"[DEBUG] RHS is a variable: {rh_list}")
        if rh_list in rh_domain:
            print(f"[DEBUG] RHS variable {rh_list} is already bound to {rh_domain[rh_list]}")
            return unify_lists(lh_list, rh_domain[rh_list], lh_domain, rh_domain)
        else:
            print(f"[DEBUG] Binding RHS variable {rh_list} to {lh_list}")
            rh_domain[rh_list] = lh_list
            return True
    
    # If we get here, try to unify the terms directly
    print(f"[DEBUG] Attempting direct term unification: {lh_list} with {rh_list}")
    return unify_terms(lh_list, rh_list, lh_domain, rh_domain)
    
    # Helper function to check if a term is a list pattern like [H|T]
    def is_list_pattern(term):
        if isinstance(term, str):
            return '|' in term and term.startswith('[') and term.endswith(']')
        return (isinstance(term, list) and len(term) >= 2 and 
                term[1] == '|' and len(term) == 3)
    
    # Helper function to parse list pattern [H|T] into (head, tail)
    def parse_list_pattern(pattern):
        if isinstance(pattern, str):
            if '|' in pattern:
                parts = pattern[1:-1].split('|', 1)
                return parts[0].strip(), parts[1].strip()
            return None, None
        elif isinstance(pattern, list) and len(pattern) == 3 and pattern[1] == '|':
            return pattern[0], pattern[2]
        return None, None
    
    # Handle empty lists
    if (lh_list == [] or lh_list == '[]') and (rh_list == [] or rh_list == '[]'):
        return True
    
    # Handle list patterns like [H|T] or [_|_]
    lh_head, lh_tail = parse_list_pattern(lh_list)
    rh_head, rh_tail = parse_list_pattern(rh_list)
    
    # Case 1: Left is a list pattern [H|T] or [_|_]
    if lh_head is not None:
        print(f"[DEBUG] Found list pattern in LHS: {lh_head}|{lh_tail}")
        
        # If right is empty, no match unless tail is also empty
        if not rh_list or rh_list == '[]':
            return lh_tail == '[]' or lh_tail == []
            
        # If right is a variable, bind it to the pattern
        if isinstance(rh_list, str) and (rh_list[0].isupper() or rh_list.startswith('_')):
            if rh_list in rh_domain:
                return unify_lists(lh_list, rh_domain[rh_list], lh_domain, rh_domain)
            else:
                # Bind the variable to the pattern
                rh_domain[rh_list] = lh_list
                return True
                
        # If right is a list, unify head and tail
        if isinstance(rh_list, list) and rh_list:
            # Unify head
            if not unify_terms(lh_head, rh_list[0], lh_domain, rh_domain):
                return False
            # Unify tail
            if lh_tail == '_':  # Anonymous variable, match anything
                return True
            if lh_tail == '[]':  # Empty tail, so list should have exactly one element
                return len(rh_list) == 1
            # Recurse with the tail
            return unify_lists(lh_tail, rh_list[1:], lh_domain, rh_domain)
    
    # Case 2: Right is a list pattern [H|T] or [_|_]
    if rh_head is not None:
        print(f"[DEBUG] Found list pattern in RHS: {rh_head}|{rh_tail}")
        return unify_lists(rh_list, lh_list, rh_domain, lh_domain)  # Swap and retry
    
    # Convert string representations to actual lists if needed
    if isinstance(lh_list, str) and lh_list.startswith('[') and lh_list.endswith(']'):
        try:
            from .expr import Expr
            print(f"[DEBUG] Parsing LHS list: {lh_list}")
            lh_expr = Expr(lh_list)
            lh_list = lh_expr.terms if hasattr(lh_expr, 'terms') else []
            print(f"[DEBUG] Parsed LHS list: {lh_list}")
        except Exception as e:
            print(f"[DEBUG] Error parsing LHS list: {e}")
            lh_list = []
    
    if isinstance(rh_list, str) and rh_list.startswith('[') and rh_list.endswith(']'):
        try:
            from .expr import Expr
            print(f"[DEBUG] Parsing RHS list: {rh_list}")
            rh_expr = Expr(rh_list)
            rh_list = rh_expr.terms if hasattr(rh_expr, 'terms') else []
            print(f"[DEBUG] Parsed RHS list: {rh_list}")
        except Exception as e:
            print(f"[DEBUG] Error parsing RHS list: {e}")
            rh_list = []
    
    # Handle cases where one is empty and the other is a variable
    if (lh_list == [] or lh_list == '[]'):
        if isinstance(rh_list, str) and (rh_list[0].isupper() or rh_list.startswith('_')):
            print(f"[DEBUG] LHS is empty, RHS is variable: {rh_list}")
            if rh_list in rh_domain:
                print(f"[DEBUG] Variable {rh_list} is bound to {rh_domain[rh_list]}")
                return unify_lists(lh_list, rh_domain[rh_list], lh_domain, rh_domain)
            else:
                rh_domain[rh_list] = []
                return True
        return rh_list == []
    
    if rh_list == []:
        if isinstance(lh_list, str) and (lh_list[0].isupper() or lh_list.startswith('_')):
            if lh_list in lh_domain:
                return unify_lists(lh_domain[lh_list], rh_list, lh_domain, rh_domain)
            else:
                lh_domain[lh_list] = []
                return True
        return False
    
    # Handle list patterns like [X|_]
    if isinstance(lh_list, list) and len(lh_list) == 2 and (lh_list[1] == '_' or lh_list[1] == '_|_[]' or lh_list[1] == '_|_[]'):
        # Pattern like [X|_]
        var = lh_list[0]
        if isinstance(var, str) and (var[0].isupper() or var.startswith('_')):
            if var in lh_domain:
                if not unify_terms(lh_domain[var], rh_list[0], lh_domain, rh_domain):
                    return False
            else:
                if isinstance(rh_list, list) and rh_list:
                    lh_domain[var] = rh_list[0] if len(rh_list) > 0 else []
                else:
                    lh_domain[var] = rh_list
            return True
    
    if isinstance(rh_list, list) and len(rh_list) == 2 and (rh_list[1] == '_' or rh_list[1] == '_|_[]' or rh_list[1] == '_|_[]'):
        # Pattern like [X|_]
        var = rh_list[0]
        if isinstance(var, str) and (var[0].isupper() or var.startswith('_')):
            if var in rh_domain:
                if not unify_terms(lh_list[0], rh_domain[var], lh_domain, rh_domain):
                    return False
            else:
                if isinstance(lh_list, list) and lh_list:
                    rh_domain[var] = lh_list[0] if len(lh_list) > 0 else []
                else:
                    rh_domain[var] = lh_list
            return True
    
    # Handle variables that might be bound to lists
    if isinstance(lh_list, str) and (lh_list[0].isupper() or lh_list.startswith('_')):
        if lh_list in lh_domain:
            return unify_lists(lh_domain[lh_list], rh_list, lh_domain, rh_domain)
        else:
            # Don't bind a variable to an empty list if we're trying to match a non-empty list
            if rh_list == []:
                lh_domain[lh_list] = []
                return True
            lh_domain[lh_list] = rh_list
            return True
    
    if isinstance(rh_list, str) and (rh_list[0].isupper() or rh_list.startswith('_')):
        if rh_list in rh_domain:
            return unify_lists(lh_list, rh_domain[rh_list], lh_domain, rh_domain)
        else:
            # Don't bind a variable to an empty list if we're trying to match a non-empty list
            if lh_list == []:
                rh_domain[rh_list] = []
                return True
            rh_domain[rh_list] = lh_list
            return True
    
    # If either is not a list at this point, they don't unify
    # If we get here, the terms don't unify
    return False
    
    # Handle string representations of lists
    if isinstance(lh_list, str):
        if lh_list == '[]':
            lh_list = []
        elif lh_list.startswith('[') and lh_list.endswith(']'):
            # Parse the list string into a Python list
            from .expr import Expr
            expr = Expr(lh_list)
            if expr.predicate == 'list':
                lh_list = expr.terms
            else:
                lh_list = [lh_list]
    
    if isinstance(rh_list, str):
        if rh_list == '[]':
            rh_list = []
        elif rh_list.startswith('[') and rh_list.endswith(']'):
            # Parse the list string into a Python list
            from .expr import Expr
            expr = Expr(rh_list)
            if expr.predicate == 'list':
                rh_list = expr.terms
            else:
                rh_list = [rh_list]
    
    # Handle variables in lists
    if isinstance(lh_list, str) and (lh_list[0].isupper() or lh_list.startswith('_')):
        if lh_list in lh_domain:
            return unify_lists(lh_domain[lh_list], rh_list, lh_domain, rh_domain)
        else:
            # Bind the variable to the other list
            lh_domain[lh_list] = rh_list
            return True
    
    if isinstance(rh_list, str) and (rh_list[0].isupper() or rh_list.startswith('_')):
        if rh_list in rh_domain:
            return unify_lists(lh_list, rh_domain[rh_list], lh_domain, rh_domain)
        else:
            # Bind the variable to the other list
            rh_domain[rh_list] = lh_list
            return True
    
    # If one is not a list at this point, they can't unify
    if not isinstance(lh_list, list) or not isinstance(rh_list, list):
        #print(f"Not both are lists: {lh_list} vs {rh_list}")
        return str(lh_list) == str(rh_list)
    
    # If both are empty lists, they unify
    if not lh_list and not rh_list:
        return True
        
    # If one is empty and the other isn't, they don't unify
    if not lh_list or not rh_list:
        #print(f"One list is empty: {lh_list} vs {rh_list}")
        return False
    
    # Check if the first elements unify
    if not unify_terms(lh_list[0], rh_list[0], lh_domain, rh_domain):
        #print(f"First elements don't unify: {lh_list[0]} vs {rh_list[0]}")
        return False
    
    # Recursively check the rest of the lists
    return unify_lists(lh_list[1:], rh_list[1:], lh_domain, rh_domain)

def unify_terms(lh, rh, lh_domain, rh_domain):
    """Unify two terms, which could be variables, constants, or lists"""
    print(f"[DEBUG] unify_terms: {lh} (type: {type(lh)}) with {rh} (type: {type(rh)})")
    
    # If both terms are the same, they unify
    if lh == rh:
        print("[DEBUG] Terms are identical, returning True")
        return True
    
    # Handle None values
    if lh is None or rh is None:
        print("[DEBUG] One term is None, returning False")
        return False
    
    # Check for variables
    if isinstance(lh, str) and (lh[0].isupper() or lh.startswith('_')):
        print(f"[DEBUG] LHS is a variable: {lh}")
        if lh in lh_domain:
            print(f"[DEBUG] LHS variable {lh} is already bound to {lh_domain[lh]}")
            # If the variable is bound to itself, we can bind it to the RHS
            if lh_domain[lh] == lh and lh != rh:
                print(f"[DEBUG] Binding variable {lh} to {rh}")
                lh_domain[lh] = rh
                return True
            # Otherwise, unify with the bound value
            return unify_terms(lh_domain[lh], rh, lh_domain, rh_domain)
        else:
            # Don't bind a variable to itself
            if lh == rh:
                print(f"[DEBUG] Variable {lh} is the same as RHS, returning True")
                return True
            # If RHS is a variable that's already bound, bind to its value
            if isinstance(rh, str) and (rh[0].isupper() or rh.startswith('_')) and rh in rh_domain:
                print(f"[DEBUG] Binding LHS variable {lh} to {rh_domain[rh]}")
                lh_domain[lh] = rh_domain[rh]
                return True
            print(f"[DEBUG] Binding LHS variable {lh} to {rh}")
            lh_domain[lh] = rh
            return True
            
    if isinstance(rh, str) and (rh[0].isupper() or rh.startswith('_')):
        print(f"[DEBUG] RHS is a variable: {rh}")
        if rh in rh_domain:
            print(f"[DEBUG] RHS variable {rh} is already bound to {rh_domain[rh]}")
            # If the variable is bound to itself, we can bind it to the LHS
            if rh_domain[rh] == rh and rh != lh:
                print(f"[DEBUG] Binding variable {rh} to {lh}")
                rh_domain[rh] = lh
                return True
            # Otherwise, unify with the bound value
            return unify_terms(lh, rh_domain[rh], lh_domain, rh_domain)
        else:
            # Don't bind a variable to itself
            if rh == lh:
                print(f"[DEBUG] Variable {rh} is the same as LHS, returning True")
                return True
            # If LHS is a variable that's already bound, bind to its value
            if isinstance(lh, str) and (lh[0].isupper() or lh.startswith('_')) and lh in lh_domain:
                print(f"[DEBUG] Binding RHS variable {rh} to {lh_domain[lh]}")
                rh_domain[rh] = lh_domain[lh]
                return True
            print(f"[DEBUG] Binding RHS variable {rh} to {lh}")
            rh_domain[rh] = lh
            return True
    
    # Handle string representations of lists and other terms
    if isinstance(lh, str):
        print(f"[DEBUG] Processing LHS string: {lh}")
        if lh.startswith('[') and lh.endswith(']'):
            from .expr import Expr
            try:
                print(f"[DEBUG] Parsing LHS as list: {lh}")
                lh_expr = Expr(lh)
                if hasattr(lh_expr, 'terms'):
                    lh = lh_expr.terms
                    print(f"[DEBUG] Parsed LHS as list: {lh}")
                else:
                    lh = [lh_expr]
            except Exception as e:
                print(f"[DEBUG] Error parsing LHS list: {e}")
                lh = []
    
    if isinstance(rh, str):
        print(f"[DEBUG] Processing RHS string: {rh}")
        if rh.startswith('[') and rh.endswith(']'):
            from .expr import Expr
            try:
                print(f"[DEBUG] Parsing RHS as list: {rh}")
                rh_expr = Expr(rh)
                if hasattr(rh_expr, 'terms'):
                    rh = rh_expr.terms
                    print(f"[DEBUG] Parsed RHS as list: {rh}")
                else:
                    rh = [rh_expr]
            except Exception as e:
                print(f"[DEBUG] Error parsing RHS list: {e}")
                rh = []
    
    # Handle Expr objects
    if hasattr(lh, 'predicate') or hasattr(rh, 'predicate'):
        print("[DEBUG] At least one term is an Expr object")
        # If both are Expr objects, check predicates and unify terms
        if hasattr(lh, 'predicate') and hasattr(rh, 'predicate'):
            if lh.predicate != rh.predicate:
                print(f"[DEBUG] Predicates don't match: {lh.predicate} vs {rh.predicate}")
                return False
            print(f"[DEBUG] Unifying Expr terms: {lh.terms} with {rh.terms}")
            return unify_lists(lh.terms, rh.terms, lh_domain, rh_domain)
        # If one is an Expr and the other is a list, convert and unify
        elif hasattr(lh, 'predicate') and isinstance(rh, list):
            print(f"[DEBUG] Unifying Expr with list: {lh.terms} with {rh}")
            return unify_lists(lh.terms, rh, lh_domain, rh_domain)
        elif hasattr(rh, 'predicate') and isinstance(lh, list):
            print(f"[DEBUG] Unifying list with Expr: {lh} with {rh.terms}")
            return unify_lists(lh, rh.terms, lh_domain, rh_domain)
        else:
            print("[DEBUG] Expr type mismatch")
            return False
    
    # Handle lists and list patterns
    if isinstance(lh, list) or isinstance(rh, list):
        print(f"[DEBUG] At least one term is a list, unifying as lists")
        # Convert to lists if they're not already
        lh_list = lh.terms if hasattr(lh, 'terms') else lh
        rh_list = rh.terms if hasattr(rh, 'terms') else rh
        
        # If either is not a list at this point, they don't unify
        if not isinstance(lh_list, list) or not isinstance(rh_list, list):
            print("[DEBUG] One term is not a list, can't unify")
            return False
            
        print(f"[DEBUG] Unifying lists: {lh_list} with {rh_list}")
        return unify_lists(lh_list, rh_list, lh_domain, rh_domain)
    
    # If we get here, the terms are atomic and not equal
    print(f"[DEBUG] Terms are atomic and not equal: {lh} != {rh}")
    return False

## unify function that will bind variables in the search to their counterparts in the tree
## it takes two pl_expr and try to match the uppercased in lh or lh.domain with their corresponding
## values in rh itself or its domain
def unify(lh, rh, lh_domain=None, rh_domain=None):
    if rh_domain is None:
        rh_domain = {}
    if lh_domain is None:
        lh_domain = {}
    
    # Debug print
    #print(f"Unifying: {lh} with {rh}")
    #print(f"LH type: {type(lh)}, RH type: {type(rh)}")
    
    # Handle direct list comparison
    if hasattr(lh, 'predicate') and hasattr(rh, 'predicate'):
        # Debug print
        #print(f"LH predicate: {lh.predicate}, RH predicate: {rh.predicate}")
        #print(f"LH terms: {lh.terms}, RH terms: {rh.terms}")
        
        # Both are empty lists
        if lh.predicate == '[]' and rh.predicate == '[]':
            #print("Both are empty lists")
            return True
            
        # One is a list and the other isn't
        if (lh.predicate == '[]' or rh.predicate == '[]'):
            #print("One is a list and the other isn't")
            return False
            
        # Both are lists (non-empty)
        if lh.predicate == 'list' and rh.predicate == 'list':
            #print("Both are non-empty lists")
            return unify_lists(lh.terms, rh.terms, lh_domain, rh_domain)
    
    # If we have terms to unify
    if hasattr(lh, 'terms') and hasattr(rh, 'terms'):
        # Check if the predicates match
        if lh.predicate != rh.predicate:
            return False
            
        nterms = len(rh.terms)
        if nterms != len(lh.terms):
            return False
        
        for i in range(nterms):
            rh_arg = rh.terms[i]
            lh_arg = lh.terms[i]
            
            if lh_arg == "_":  # Anonymous variable, matches anything
                continue
                
            # Handle list terms in arguments
            if isinstance(lh_arg, list) or isinstance(rh_arg, list):
                lh_list = lh_arg if isinstance(lh_arg, list) else [lh_arg]
                rh_list = rh_arg if isinstance(rh_arg, list) else [rh_arg]
                if not unify_lists(lh_list, rh_list, lh_domain, rh_domain):
                    return False
                continue
                
            # Handle variables
            if is_variable(lh_arg):
                if lh_arg in lh_domain:
                    # If the variable is already bound, use its value
                    lh_val = lh_domain[lh_arg]
                    # Resolve nested variable references
                    while isinstance(lh_val, str) and is_variable(lh_val) and lh_val in lh_domain:
                        lh_val = lh_domain[lh_val]
                    if not unify_terms(lh_val, rh_arg, lh_domain, rh_domain):
                        return False
                else:
                    # Bind the variable to the corresponding term
                    # But first, check if the RHS is a variable that's already bound
                    if is_variable(rh_arg) and rh_arg in rh_domain:
                        rh_val = rh_domain[rh_arg]
                        lh_domain[lh_arg] = rh_val
                    else:
                        lh_domain[lh_arg] = rh_arg
                continue
                
            if is_variable(rh_arg):
                if rh_arg in rh_domain:
                    rh_val = rh_domain[rh_arg]
                    # Resolve nested variable references
                    while isinstance(rh_val, str) and is_variable(rh_val) and rh_val in rh_domain:
                        rh_val = rh_domain[rh_val]
                    if not unify_terms(lh_arg, rh_val, lh_domain, rh_domain):
                        return False
                else:
                    # Bind the variable to the corresponding term
                    rh_domain[rh_arg] = lh_arg
                continue
                
            # For non-variable terms, they must be equal
            if isinstance(lh_arg, (int, float)) and isinstance(rh_arg, (int, float)):
                if abs(lh_arg - rh_arg) > 1e-9:  # Handle floating point comparison
                    return False
            elif str(lh_arg) != str(rh_arg):
                return False
    
    return True
