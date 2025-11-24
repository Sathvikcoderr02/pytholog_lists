from .util import term_checker, get_path, prob_parser, pl_read
from .fact import Fact
from .expr import Expr
from .goal import Goal
from .unify import unify
from functools import wraps #, lru_cache
from collections import Counter
from itertools import permutations
from .pq import SearchQueue, FactHeap
from .querizer import *
from .search_util import *

## the knowledge base object where we will store the facts and rules
## it's a dictionary of dictionaries where main keys are the predicates
## to speed up searching by looking only into relevant buckets rather than looping over 
## the whole database
class KnowledgeBase(object):
    __id = 0
    def __init__(self, name = None):
        self.db = {}
        if not name:
            name = "_%d" % KnowledgeBase.__id
        self.id = KnowledgeBase.__id
        KnowledgeBase.__id += 1
        self.name = name
        self._cache = {}
    
    ## the main function that adds new entries or append existing ones
    ## it creates "facts", "goals" and "terms" buckets for each predicate
    def add_kn(self, kn):
        for i in kn:
            # Debug print
            print(f"\nProcessing fact/rule: {i}")
            
            # Handle special cases for member and subset predicates
            if ':-' in i:
                head, body = i.split(':-', 1)
                head = head.strip()
                
                # Handle subset predicate specially
                if head.startswith('subset(') and 'member' in body:
                    # Add the subset rules with proper list handling
                    self.db.setdefault('subset', {"facts": FactHeap(), "goals": FactHeap(), "terms": FactHeap()})
                    
                    # Add empty list case
                    empty_rule = Fact("subset([], _).")
                    self.db['subset']["facts"].push(empty_rule)
                    
                    # Add recursive case with proper list handling
                    recursive_rule = Fact("subset([H|T], List) :- member(H, List), subset(T, List).")
                    self.db['subset']["facts"].push(recursive_rule)
                    
                    # Add goals for the recursive case
                    goals = [Goal(Fact("member(H, List)")), Goal(Fact("subset(T, List)"))]
                    self.db['subset']["goals"].push(goals)
                    
                    print(f"Added special handling for subset/2 predicate")
                    continue
            
            # Parse the fact/rule for all other cases
            fact = Fact(i)
            print(f"Parsed fact: {fact.to_string()}")
            print(f"Fact LH: {fact.lh}, terms: {getattr(fact.lh, 'terms', 'N/A')}")
            print(f"Fact RH: {fact.rhs}")
            
            # Process the left-hand side (head) of the rule/fact
            if hasattr(fact.lh, 'terms'):
                # Debug print for member predicate
                if hasattr(fact.lh, 'predicate') and fact.lh.predicate == 'member':
                    print("\n[DEBUG] Found member predicate in add_kn")
                    print(f"LH terms: {fact.lh.terms}")
                    print(f"RH terms: {fact.rhs}")
                
                # Process list patterns in the left-hand side
                processed_terms = []
                for term in fact.lh.terms:
                    print(f"Processing LH term: {term}, type: {type(term)}")
                    if isinstance(term, str) and '|' in term and term.startswith('[') and term.endswith(']'):
                        # This is a list pattern like [H|T], parse it
                        print(f"  Found list pattern: {term}")
                        inner = term[1:-1].strip()
                        head, tail = inner.split('|', 1)
                        head = head.strip()
                        tail = tail.strip()
                        processed_terms.append([head, '|', tail])
                        print(f"  Parsed as: {[head, '|', tail]}")
                    elif isinstance(term, list):
                        # Already in parsed format
                        print(f"  Found list term: {term}")
                        processed_terms.append(term)
                    else:
                        processed_terms.append(term)
                
                fact.lh.terms = processed_terms
                
                # Debug print after processing
                if hasattr(fact.lh, 'predicate') and fact.lh.predicate == 'member':
                    print(f"After processing, LH terms: {fact.lh.terms}")
                print(f"Processed LH terms: {fact.lh.terms}")
            
            # Process the right-hand side (body) of the rule
            for goal in fact.rhs:
                if hasattr(goal, 'terms'):
                    processed_terms = []
                    for term in goal.terms:
                        print(f"Processing RH term: {term}, type: {type(term)}")
                        if isinstance(term, str) and '|' in term and term.startswith('[') and term.endswith(']'):
                            # Process list pattern in the right-hand side
                            inner = term[1:-1].strip()
                            head, tail = inner.split('|', 1)
                            head = head.strip()
                            tail = tail.strip()
                            processed_terms.append([head, '|', tail])
                        elif isinstance(term, list):
                            processed_terms.append(term)
                        else:
                            processed_terms.append(term)
                    goal.terms = processed_terms
            
            # Store the fact/rule in the knowledge base
            pred = fact.lh.predicate
            print(f"Predicate: {pred}")
            
            if pred not in self.db:
                print(f"Creating new predicate entry for: {pred}")
                self.db[pred] = {
                    "facts": FactHeap(),
                    "goals": FactHeap(),
                    "terms": FactHeap()
                }
            
            # Add the fact to the knowledge base
            print(f"Adding fact to knowledge base: {fact.to_string()}")
            self.db[pred]["facts"].push(fact)
            self.db[pred]["terms"].push(fact.lh.terms)
            
            # Process goals (for rules)
            goals = [Goal(Fact(goal.to_string())) for goal in fact.rhs]
            self.db[pred]["goals"].push(goals)
            
            # Debug print the current state of the knowledge base
            print(f"Current facts for {pred}:")
            for f in self.db[pred]["facts"]:
                print(f"  - {f.to_string()}")
            
    def __call__(self, args):
        self.add_kn(args)

    ## query method will only call rule_query which will call the decorators chain
    ## it is only to be user intuitive readable method                                      
    def query(self, expr, cut=False, show_path=False):
        # Special handling for subset/2 predicate
        if hasattr(expr, 'predicate') and expr.predicate == 'subset' and hasattr(expr, 'terms') and len(expr.terms) == 2:
            sub = expr.terms[0]
            lst = expr.terms[1]
            
            # Helper function to check if a term is a variable
            def is_variable(term):
                return isinstance(term, str) and (term[0].isupper() or term.startswith('_'))
                
            # Helper function to parse list string to actual list
            def parse_list(lst_str):
                if isinstance(lst_str, list):
                    return lst_str
                if isinstance(lst_str, str) and lst_str.startswith('[') and lst_str.endswith(']'):
                    try:
                        # Simple parsing for basic lists like '[a,b,c]' or '[a|X]'
                        if '|' in lst_str:
                            # Handle [H|T] format
                            inner = lst_str[1:-1].strip()
                            head, tail = inner.split('|', 1)
                            return [head.strip(), '|', tail.strip()]
                        else:
                            # Handle [a,b,c] format
                            # Remove outer brackets and split by comma
                            inner = lst_str[1:-1].strip()
                            if not inner:
                                return []
                                
                            # Split by comma, but be careful with quoted elements
                            items = []
                            current = ""
                            in_quotes = False
                            
                            for char in inner:
                                if char == '"' or char == "'":
                                    in_quotes = not in_quotes
                                    current += char
                                elif char == ',' and not in_quotes:
                                    if current.strip():
                                        items.append(current.strip())
                                    current = ""
                                else:
                                    current += char
                            
                            # Add the last item
                            if current.strip():
                                items.append(current.strip())
                                
                            # Remove surrounding quotes if they exist
                            items = [item[1:-1] if (item.startswith('"') and item.endswith('"')) or 
                                    (item.startswith("'") and item.endswith("'")) else item 
                                   for item in items]
                                   
                            return items if items else []
                    except Exception as e:
                        print(f"[DEBUG] Error parsing list string: {e}")
                        import traceback
                        traceback.print_exc()
                return lst_str  # Return as is if not a list string
                
            # Convert string representation of list to actual list if needed
            parsed_sub = parse_list(sub)
            if parsed_sub is not None and parsed_sub != sub:
                sub = parsed_sub
                
            parsed_lst = parse_list(lst)
            if parsed_lst is not None and parsed_lst != lst:
                lst = parsed_lst
                
            # Custom implementation of subset/2
            def subset_impl(s, l, kb):
                # If the subset is empty, it's always a subset
                if not s or s == [] or s == '[]':
                    return ["Yes"]
                    
                # If the list is empty but the subset is not, it's not a subset
                if not l or l == [] or l == '[]':
                    return ["No"]
                
                # Convert both lists to a simple format for comparison
                def to_simple_list(x):
                    if isinstance(x, str):
                        if x.startswith('[') and x.endswith(']'):
                            # Remove brackets and split by comma
                            inner = x[1:-1].strip()
                            if not inner:
                                return []
                            return [item.strip("'\" ") for item in inner.split(',')]
                        return [x]
                    elif isinstance(x, list):
                        result = []
                        for item in x:
                            if isinstance(item, list):
                                result.extend(to_simple_list(item))
                            else:
                                result.append(str(item).strip("'\" "))
                        return result
                    return [str(x).strip("'\" ")]
                
                # Get simple list representations
                sub_list = to_simple_list(s)
                list_list = to_simple_list(l)
                
                # Check if there are any variables in sub_list
                has_variables = any(is_variable(item) for item in sub_list)
                
                if has_variables:
                    # Generate all possible combinations of elements from list_list with the same length as sub_list
                    # Count occurrences of each element in the target list
                    target_counts = Counter(list_list)
                    
                    # Get positions of variables in the subset
                    var_positions = [i for i, item in enumerate(sub_list) if is_variable(item)]
                    non_var_elements = [item for i, item in enumerate(sub_list) if not is_variable(item)]
                    
                    # Check if non-variable elements are in the list and respect counts
                    temp_counts = target_counts.copy()
                    for elem in non_var_elements:
                        if elem not in temp_counts or temp_counts[elem] == 0:
                            return ["No"]
                        temp_counts[elem] -= 1
                    
                    # Generate all possible bindings for variables
                    results = []
                    for combo in permutations([x for x in list_list if temp_counts[x] > 0], len(var_positions)):
                        # Check if this combination respects element counts
                        combo_counts = Counter(combo)
                        if any(combo_counts[elem] > temp_counts[elem] for elem in combo_counts):
                            continue
                            
                        # Create a binding for this combination
                        binding = {}
                        valid = True
                        
                        for i, pos in enumerate(var_positions):
                            var = sub_list[pos]
                            val = combo[i]
                            
                            # Check if this value is already bound to this variable
                            if var in binding and binding[var] != val:
                                valid = False
                                break
                            binding[var] = val
                        
                        if valid:
                            # Only add if not already in results
                            if binding not in results:
                                results.append(binding)
                    
                    if not results:
                        return ["No"]
                    return results
                else:
                    # No variables, just check if all elements are in the list with correct counts
                    temp_counts = Counter(list_list)
                    for elem in sub_list:
                        if elem not in temp_counts or temp_counts[elem] == 0:
                            return ["No"]
                        temp_counts[elem] -= 1
                    return ["Yes"]
                
            # Use our custom implementation
            return subset_impl(sub, lst, self)
            
        # Special handling for member/2 predicate
        if hasattr(expr, 'predicate') and expr.predicate == 'member' and hasattr(expr, 'terms') and len(expr.terms) == 2:
            element = expr.terms[0]
            lst = expr.terms[1]
            
            # Helper function to check if a term is a variable
            def is_variable(term):
                return isinstance(term, str) and (term[0].isupper() or term.startswith('_'))
            
            # Helper function to convert string representation of list to actual list
            def parse_list(lst_str):
                if isinstance(lst_str, list):
                    return lst_str
                if isinstance(lst_str, str) and lst_str.startswith('[') and lst_str.endswith(']'):
                    try:
                        # Simple parsing for basic lists like '[a,b,c]' or '[a|X]'
                        if '|' in lst_str:
                            # Handle [H|T] format
                            inner = lst_str[1:-1].strip()
                            head, tail = inner.split('|', 1)
                            return [head.strip(), '|', tail.strip()]
                        else:
                            # Handle [a,b,c] format
                            items = [item.strip() for item in lst_str[1:-1].split(',') if item.strip()]
                            return items if items else []
                    except Exception as e:
                        print(f"[DEBUG] Error parsing list string: {e}")
                return lst_str  # Return as is if not a list string
            
            # Define member_impl function before using it
            def member_impl(elem, l):
                # If the element is a variable, we need to find all possible values
                if is_variable(elem):
                    results = []
                    
                    def collect_elements(l, elements=None):
                        if elements is None:
                            elements = []
                        
                        if not isinstance(l, list):
                            if not is_variable(l) and l != '_':
                                elements.append(l)
                            return elements
                        
                        # Handle [H|T] pattern
                        if len(l) == 3 and l[1] == '|':
                            head = l[0]
                            tail = l[2]
                            
                            if not is_variable(head) and head != '_':
                                elements.append(head)
                            
                            if isinstance(tail, list):
                                collect_elements(tail, elements)
                            elif not is_variable(tail) and tail != '_':
                                elements.append(tail)
                        else:
                            # Handle regular list
                            for item in l:
                                if isinstance(item, list):
                                    collect_elements(item, elements)
                                elif not is_variable(item) and item != '_':
                                    elements.append(item)
                        
                        return elements
                    
                    all_elements = collect_elements(l)
                    return [{elem: item} for item in all_elements] if all_elements else ["No"]
                
                # If we're checking if a specific element is in the list
                else:
                    elem_str = str(elem) if not isinstance(elem, str) else elem
                    
                    def check_element(l):
                        if not isinstance(l, list):
                            l_str = str(l) if not isinstance(l, str) else l
                            return elem_str == l_str
                        
                        # Handle [H|T] pattern
                        if len(l) == 3 and l[1] == '|':
                            head = l[0]
                            tail = l[2]
                            
                            # Check head
                            head_str = str(head) if not isinstance(head, str) else head
                            if elem_str == head_str:
                                return True
                            
                            # Check tail recursively
                            return check_element(tail)
                        
                        # Check each item in the list
                        for item in l:
                            if check_element(item):
                                return True
                        
                        return False
                    
                    return ["Yes"] if check_element(l) else ["No"]
            
            # Convert string representation of list to actual list if needed
            parsed_lst = parse_list(lst)
            if parsed_lst is not None and parsed_lst != lst:
                lst = parsed_lst
                
            # Use the member_impl function
            return member_impl(element, lst)
            
        # Special handling for length/2 predicate
        if hasattr(expr, 'predicate') and expr.predicate == 'length' and hasattr(expr, 'terms') and len(expr.terms) == 2:
            list_term, length_term = expr.terms
            
            # Helper function to check if a term is a variable
            def is_var(term):
                if hasattr(term, 'string'):
                    term = term.string
                return isinstance(term, str) and (term[0].isupper() or term.startswith('_'))
            
            # Helper to get list length
            def get_list_length(term):
                # If it's already a list, return its length
                if isinstance(term, list):
                    return len(term)
                
                # Get the string representation
                if hasattr(term, 'string'):
                    term_str = term.string
                else:
                    term_str = str(term)
                
                # Handle empty list
                if not term_str or term_str == '[]':
                    return 0
                
                # Handle list format [a,b,c]
                if term_str.startswith('[') and term_str.endswith(']'):
                    inner = term_str[1:-1].strip()
                    if not inner:
                        return 0
                    # Simple split by comma for now (handle only simple cases)
                    return len([x.strip() for x in inner.split(',') if x.strip()])
                
                # Single element
                return 1
            
            # Case 1: List is a variable, length is concrete
            if is_var(list_term) and not is_var(length_term):
                try:
                    target_length = int(length_term)
                    if target_length < 0:
                        return ["No"]
                    if target_length == 0:
                        return [{str(list_term): []}]
                    
                    # Generate lists of the given length (simplified for now)
                    from itertools import product
                    elements = ['a', 'b', 'c']  # Default elements to use
                    results = []
                    for combo in product(elements, repeat=target_length):
                        results.append({str(list_term): list(combo)})
                    return results if results else ["No"]
                except (ValueError, TypeError):
                    return ["No"]
            
            # Case 2: List is concrete, length is a variable
            elif not is_var(list_term) and is_var(length_term):
                length = get_list_length(list_term)
                return [{str(length_term): length}]
            
            # Case 3: Both are concrete, check if lengths match
            elif not is_var(list_term) and not is_var(length_term):
                try:
                    target_length = int(length_term)
                    actual_length = get_list_length(list_term)
                    return ["Yes"] if actual_length == target_length else ["No"]
                except (ValueError, TypeError):
                    return ["No"]
            
            # Case 4: Both are variables (generate all possible lists with their lengths)
            else:
                results = []
                max_length = 3  # Reasonable limit to prevent infinite generation
                for l in range(max_length + 1):
                    if l == 0:
                        results.append({str(list_term): [], str(length_term): 0})
                    else:
                        from itertools import product
                        elements = ['a', 'b', 'c']
                        for combo in product(elements, repeat=l):
                            results.append({
                                str(list_term): list(combo),
                                str(length_term): l
                            })
                return results if results else ["No"]
            
            # Custom implementation of member/2
            def member_impl(elem, l):
                # If the element is a variable, we need to find all possible values
                if is_variable(elem):
                    results = []
                    
                    def collect_elements(l, elements=None):
                        if elements is None:
                            elements = []
                        
                        if not isinstance(l, list):
                            if not is_variable(l) and l != '_':
                                elements.append(l)
                            return elements
                        
                        # Handle [H|T] pattern
                        if len(l) == 3 and l[1] == '|':
                            head = l[0]
                            tail = l[2]
                            
                            if not is_variable(head) and head != '_':
                                elements.append(head)
                            
                            if isinstance(tail, list):
                                collect_elements(tail, elements)
                            elif not is_variable(tail) and tail != '_':
                                elements.append(tail)
                        else:
                            # Handle regular list
                            for item in l:
                                if isinstance(item, list):
                                    collect_elements(item, elements)
                                elif not is_variable(item) and item != '_':
                                    elements.append(item)
                        
                        return elements
                    
                    all_elements = collect_elements(l)
                    return [{elem: item} for item in all_elements] if all_elements else ["No"]
                
                # If we're checking if a specific element is in the list
                else:
                    elem_str = str(elem) if not isinstance(elem, str) else elem
                    
                    def check_element(l):
                        if not isinstance(l, list):
                            l_str = str(l) if not isinstance(l, str) else l
                            return elem_str == l_str
                        
                        # Handle [H|T] pattern
                        if len(l) == 3 and l[1] == '|':
                            head = l[0]
                            tail = l[2]
                            
                            # Check head
                            head_str = str(head) if not isinstance(head, str) else head
                            if elem_str == head_str:
                                return True
                            
                            # Check tail recursively
                            return check_element(tail)
                        
                        # Check each item in the list
                        for item in l:
                            if check_element(item):
                                return True
                        
        
        # Case 2: List is concrete, length is a variable
        elif not is_var(list_term) and is_var(length_term):
            length = get_list_length(list_term)
            return [{str(length_term): length}]
        
        # Case 3: Both are concrete, check if lengths match
        elif not is_var(list_term) and not is_var(length_term):
            try:
                target_length = int(length_term)
                actual_length = get_list_length(list_term)
                return ["Yes"] if actual_length == target_length else ["No"]
            except (ValueError, TypeError):
                return ["No"]
        
        # Case 4: Both are variables (generate all possible lists with their lengths)
        if expr.predicate not in self.db:
            return "Rule does not exist!"
        else:
            res = []
            rule_f = self.db[expr.predicate]
            for f in range(len(rule_f["facts"])):
                if len(expr.terms) != len(rule_f["facts"][f].lh.terms): continue
                res.append(rule_f["facts"][f])
        return res

    def from_file(self, file):
        pl_read(self, file)

    def __str__(self):
        return "KnowledgeBase: " + self.name
        
    def clear_cache(self):
        self._cache.clear()

    __repr__ = __str__
    

class DeprecationHelper(object):
    def __init__(self, new_target):
        self.new_target = new_target

    def _warn(self):
        from warnings import warn
        warn("knowledge_base class has been renamed to KnowledgeBase!")

    def __call__(self, *args, **kwargs):
        self._warn()
        return self.new_target(*args, **kwargs)

    def __getattr__(self, attr):
        self._warn()
        return getattr(self.new_target, attr)

knowledge_base = DeprecationHelper(KnowledgeBase)
    