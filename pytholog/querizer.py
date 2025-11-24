from functools import wraps
from .util import term_checker, get_path, prob_parser, is_number, is_variable, answer_handler
from .fact import Fact
from .goal import Goal
from .expr import Expr
from .unify import unify, is_variable, unify_terms, unify_lists
from .search_util import fact_binary_search
import re
from .pq import SearchQueue
from .search_util import *

## memory decorator which will be called first once .query() method is called
## it takes the Expr and checks in cache {} whether it exists or not
def memory(querizer):
    #cache = {}
    @wraps(querizer)
    def memorize_query(kb, arg1, cut, show_path):
        temp_cache = {}
        
        # Check if the query is in the cache
        #key = (arg1.predicate, tuple(arg1.terms) if hasattr(arg1, 'terms') else ())
        #if key in cache:
        #    return cache[key]
        
        # If not in cache, execute the query
        result = querizer(kb, arg1, cut, show_path)
        
        # Cache the result
        #cache[key] = result
        
        # Process the result to handle variable bindings
        if result is None:
            return ["No"]
            
        if result and result != ["No"] and result != ["Yes"] and result != ["Yes."] and result != ["No."]:
            new_result = []
            if isinstance(result, list):
                for d in result:
                    if d is None:
                        continue
                    if isinstance(d, dict):
                        new_d = {}
                        for k, v in d.items():
                            if isinstance(v, str) and v.startswith('_') and v[1:].isdigit():
                                continue  # Skip internal variables
                            new_d[k] = v
                        if new_d:  # Only add if there are non-internal variables
                            new_result.append(new_d)
                    elif isinstance(d, str) and (d == "Yes" or d == "No" or d == "Yes." or d == "No."):
                        return [d]
                return new_result if new_result else ["Yes"]
        return result if result is not None else ["No"]             
        return temp_cache    
    return memorize_query

## querizer decorator is called whenever there's a new query
## it wraps two functions: simple and rule query
## simple_query() only searched facts not rules while
## rule_query() searches rules
## this can help speed up search and querizer orchestrate the function to be called
def querizer(simple_query):
    def wrap(rule_query):
        @wraps(rule_query)
        def prepare_query(kb, arg1, cut, show_path):
            pred = arg1.predicate
            if pred in kb.db:
                goals_len = 0.0
                for i in kb.db[pred]["goals"]:
                    goals_len += len(i)
                if goals_len == 0:
                    return simple_query(kb, arg1)
                else:
                    return rule_query(kb, arg1, cut, show_path)
        return prepare_query 
    return wrap 

## simple function it unifies the query with the corresponding facts
def simple_query(kb, expr):
    from .expr import Expr
    
    pred = expr.predicate
    
    # Debug print
    #print(f"\nSimple query for predicate: {pred}, terms: {getattr(expr, 'terms', [])}")
    
    # Special handling for empty list queries
    if pred == '[]' or (hasattr(expr, 'terms') and expr.terms == []):
        # Check if we have an empty list fact
        if pred in kb.db and kb.db[pred]["facts"]:
            return ["Yes"]
        return ["No"]
    
    # Special handling for member/2 predicate - always use our custom implementation
    if pred == 'member' and hasattr(expr, 'terms') and len(expr.terms) == 2:
        element = expr.terms[0]
        lst = expr.terms[1]
        
        print(f"\n[DEBUG] Member query - Element: {element} (type: {type(element)}), List: {lst} (type: {type(lst)})")
        
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
        
        # Convert string representation of list to actual list if needed
        parsed_lst = parse_list(lst)
        if parsed_lst is not None and parsed_lst != lst:
            lst = parsed_lst
        
        # Custom implementation of member/2 that works with the knowledge base
        def member_impl(elem, l):
            print(f"[DEBUG] member_impl({elem}, {l}) (type: {type(l)})")
            
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
                print(f"[DEBUG] All elements in list: {all_elements}")
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
                
                result = check_element(l)
                print(f"[DEBUG] Element {elem} in list: {result}")
                return ["Yes"] if result else ["No"]
        
        # Use our custom implementation and bypass standard unification
        result = member_impl(element, lst)
        print(f"[DEBUG] Member result (custom): {result}")
        
        # If we're checking for a specific element and got 'No', try the standard unification
        if result == ["No"] and not is_variable(element):
            print("[DEBUG] No match found with custom implementation, trying standard unification...")
            pass  # Let the standard unification handle it
        else:
            return result
        
        # Helper function to get all elements from a list, handling nested lists and patterns
        def get_all_elements(lst_pattern):
            if not isinstance(lst_pattern, list):
                return [lst_pattern]
                
            elements = []
            
            # Handle list patterns like [H|T]
            if len(lst_pattern) == 3 and lst_pattern[1] == '|':
                head = lst_pattern[0]
                tail = lst_pattern[2]
                
                # Add the head if it's not an anonymous variable
                if head != '_' and not (isinstance(head, str) and head.startswith('_')):
                    elements.append(head)
                
                # Recursively get elements from the tail
                if tail != '[]' and tail != [] and tail != '_':
                    if isinstance(tail, list):
                        elements.extend(get_all_elements(tail))
                    else:
                        elements.append(tail)
            else:
                # Regular list, process each item
                for item in lst_pattern:
                    if item == '_' or (isinstance(item, str) and item.startswith('_')):
                        continue
                    if isinstance(item, list):
                        elements.extend(get_all_elements(item))
                    else:
                        elements.append(item)
            
            return elements
        
        # If we have a concrete list, process it
        if isinstance(lst, list):
            print(f"[DEBUG] Processing as list: {lst}")
            
            # Get all elements from the list, handling nested lists and patterns
            all_elements = get_all_elements(lst)
            print(f"[DEBUG] All elements in list: {all_elements}")
            
            # If the element is a variable, return all elements in the list
            if isinstance(element, str) and (element[0].isupper() or element.startswith('_')):
                print(f"[DEBUG] Variable element {element}, returning all items")
                
                if not all_elements:
                    print("[DEBUG] No valid items, returning ['No']")
                    return ["No"]
                
                # Create result with variable bindings
                result = []
                for item in all_elements:
                    if item is None:
                        continue
                    # Clean up the item (remove quotes if any)
                    if isinstance(item, str):
                        item = item.strip("'\"")
                    result.append({element: item})
                
                print(f"[DEBUG] Returning result: {result}")
                return result if result else ["No"]
            
            # If the element is a value, check if it's in the list
            else:
                print(f"[DEBUG] Checking if {element} is in {all_elements}")
                # Clean up the element (remove quotes if any)
                element_str = str(element).strip("'\"")
                for item in all_elements:
                    if item is None:
                        continue
                    item_str = str(item).strip("'\"")
                    if item_str == element_str:
                        print(f"[DEBUG] Found match: {item}")
                        return ["Yes"]
                
                print("[DEBUG] No match found")
                return ["No"]
                
        # If the list is a variable or pattern, use the knowledge base rules
        else:
            print(f"[DEBUG] Using knowledge base rules for member/2")
            
            # Check if we have member/2 rules in the knowledge base
            if 'member' in kb.db and kb.db['member']["facts"]:
                print("[DEBUG] Found member/2 facts in knowledge base")
                
                # If the element is a variable, we need to find all possible bindings
                if isinstance(element, str) and (element[0].isupper() or element.startswith('_')):
                    print(f"[DEBUG] Finding all bindings for {element} in {lst}")
                    
                    # Get all elements from the list if it's a concrete list
                    if isinstance(lst, list):
                        all_elements = get_all_elements(lst)
                        print(f"[DEBUG] All elements in list: {all_elements}")
                        
                        if not all_elements:
                            return ["No"]
                            
                        # Return all elements as bindings
                        return [{element: item} for item in all_elements]
                    
                    # If the list is a variable, we can't determine the elements
                    else:
                        print("[WARNING] Cannot determine elements of non-concrete list")
                        return ["No"]
                
                # If we're checking for a specific element
                else:
                    # Check if the element is in the list
                    if isinstance(lst, list):
                        all_elements = get_all_elements(lst)
                        return ["Yes"] if str(element).strip("'\"") in all_elements else ["No"]
                    else:
                        # We can't determine if the element is in a non-concrete list
                        # So we'll say "Yes" to allow for the possibility
                        return ["Yes"]
            
            # If no member/2 rules are defined, use default behavior
            else:
                print("[WARNING] No member/2 facts found in knowledge base")
                return ["No"]
        
        # If we get here and the list is a variable, we need to use the knowledge base
        if isinstance(lst, str) and (lst[0].isupper() or lst.startswith('_')):
            print(f"[DEBUG] List is a variable: {lst}, using knowledge base")
            # This is a variable, so we need to use the knowledge base
            
    # If the predicate is not in the knowledge base, return 'No'
    if pred not in kb.db:
        #print(f"Predicate '{pred}' not found in knowledge base")
        return ["No"]
        
    search_base = kb.db[pred]["facts"]
    result = []
    
    # If there are no facts for this predicate, return 'No'
    if not search_base:
        #print(f"No facts found for predicate: {pred}")
        return ["No"]
        
    # Special handling for member/2 predicate to find all solutions
    if pred == 'member' and hasattr(expr, 'terms') and len(expr.terms) == 2:
        element = expr.terms[0]
        lst = expr.terms[1]
        
        # If we're looking for all elements in a list (member(X, [a,b,c]))
        if isinstance(element, str) and (element[0].isupper() or element.startswith('_')) and isinstance(lst, list):
            # Get all non-internal elements from the list
            elements = [item for item in lst if item is not None and not (isinstance(item, str) and (item.startswith('_') or item == ''))]
            if not elements:
                return ["No"]
            # Return each element as a separate solution
            return [{element: item} for item in elements]
    
    # Special handling for member predicate
    if pred == 'member':
        #print("Processing member predicate")
        if len(expr.terms) != 2:
            return ["No"]
            
        # Get the element and list from the query
        elem = expr.terms[0]
        lst = expr.terms[1]
        
        # If the list is a variable, we can't proceed
        if isinstance(lst, str) and (lst[0].isupper() or lst.startswith('_')):
            return ["No"]
            
        # If the list is a string representation, convert it to a list
        if isinstance(lst, str) and lst.startswith('[') and lst.endswith(']'):
            from .expr import Expr
            lst_expr = Expr(lst)
            if hasattr(lst_expr, 'terms'):
                lst = lst_expr.terms
            else:
                lst = []
        
        # If we have a list, check if the element is in it
        if isinstance(lst, list):
            # If the element is a variable, return all elements in the list
            if isinstance(elem, str) and (elem[0].isupper() or elem.startswith('_')):
                return [{"X": item} for item in lst] or ["No"]
            # If the element is a value, check if it's in the list
            elif elem in lst:
                return ["Yes"]
            else:
                return ["No"]
    
    # Special handling for empty_list predicate with empty list term
    if pred == 'empty_list':
        #print("Checking empty_list facts")
        for fact in search_base:
            # Check if the fact has no terms or has an empty list term
            if not hasattr(fact.lh, 'terms') or fact.lh.terms == []:
                return ["Yes"]
                
            # Check if the fact has a single term that's an empty list
            if len(fact.lh.terms) == 1:
                term = fact.lh.terms[0]
                if term == '[]' or term == [] or (hasattr(term, 'predicate') and term.predicate == '[]'):
                    return ["Yes"]
                    
        return ["No"]
    
    # Special handling for member/2 predicate with variables
    if pred == 'member' and hasattr(expr, 'terms') and len(expr.terms) == 2:
        element = expr.terms[0]
        lst = expr.terms[1]
        
        # If the list is a variable, we need to find all possible lists in the KB
        if isinstance(lst, str) and (lst[0].isupper() or lst.startswith('_')):
            # Find all facts that could unify with this query
            for fact in search_base:
                try:
                    fact_expr = Expr(fact.to_string())
                    if fact_expr.predicate != pred or len(fact_expr.terms) != 2:
                        continue
                        
                    res = {}
                    unified = unify(expr, fact_expr, res, {})
                    
                    if unified:
                        # If there are no variables in the query, just return 'Yes'
                        if not any(is_variable(term) for term in expr.terms):
                            return ["Yes"]
                            
                        # Otherwise, collect the variable bindings
                        if res:
                            # Filter out internal variables (starting with '_')
                            filtered_res = {k: v for k, v in res.items() 
                                         if not k.startswith('_') and not (isinstance(v, str) and v.startswith('_'))}
                            if filtered_res:  # Only add if there are variables to return
                                result.append(filtered_res)
                except Exception as e:
                    #print(f"Error processing fact {fact}: {e}")
                    continue
                    
            return result if result else ["No"]
    
    # Get the index term for binary search if it's not a variable
    if hasattr(expr, 'index') and expr.index < len(expr.terms):
        ind = expr.terms[expr.index]
        if not is_variable(ind):
            key = ind
            first, last = fact_binary_search(search_base, key)
        else:
            first, last = (0, len(search_base))
    else:
        first, last = (0, len(search_base))
    
    # Try to unify with each fact in the search range
    for i in range(first, last):
        fact = search_base[i]
        res = {}
        
        # Skip facts that can't possibly match
        if hasattr(fact, 'predicate') and hasattr(expr, 'predicate') and fact.predicate != expr.predicate:
            continue
            
        # Convert the fact to an Expr for unification
        try:
            fact_expr = Expr(fact.to_string())
            
            # Debug print
            #print(f"Trying to unify query: {expr} with fact: {fact_expr}")
            
            # Try to unify the query with the fact
            unified = unify(expr, fact_expr, res, {})
            
            if unified:
                # If there are no variables in the query, just return 'Yes'
                if not any(is_variable(term) for term in expr.terms):
                    return ["Yes"]
                    
                # Otherwise, collect the variable bindings
                if res:
                    # Filter out internal variables (starting with '_')
                    filtered_res = {k: v for k, v in res.items() 
                                 if not k.startswith('_') and not (isinstance(v, str) and v.startswith('_'))}
                    if filtered_res:  # Only add if there are variables to return
                        result.append(filtered_res)
                else:
                    result.append("Yes")
        except Exception as e:
            #print(f"Error processing fact {fact}: {e}")
            continue
    
    # If we found results, return them; otherwise, return 'No'
    return result if result else ["No"]

## rule_query() is the main search function
@memory
@querizer(simple_query)
def rule_query(kb, expr, cut, show_path):
    #pdb.set_trace() # I used to trace every step in the search that consumed me to figure out :D
    rule = Fact(expr.to_string()) # change expr to rule class
    answer = []
    path = []
    ## start from a random point (goal) outside the tree
    start = Goal(Fact("start(search):-from(random_point)"))
    ## put the expr as a goal in the random point to connect it with the tree
    start.fact.rhs = [expr]
    queue = SearchQueue() ## start the queue and fill with first random point
    queue.push(start)
    while not queue.empty: ## keep searching until it is empty meaning nothing left to be searched
        current_goal = queue.pop()
        if current_goal.ind >= len(current_goal.fact.rhs): ## all rule goals have been searched
            if current_goal.parent == None: ## no more parents 
                if current_goal.domain:  ## if there is an answer return it
                    answer.append(current_goal.domain)
                    if cut: break
                else: 
                    answer.append("Yes") ## if no returns Yes
                continue ## if no answer found go back to the parent a step above again    
            
            ## father which is the main rule takes unified child's domain from facts
            child_to_parent(current_goal, queue)
            if show_path: path.append(current_goal.domain)
            continue
        
        ## get the rh expr from the current goal to look for its predicate in database
        rule = current_goal.fact.rhs[current_goal.ind]
        
        ## Probabilities and numeric evaluation
        if rule.predicate == "": ## if there is no predicate
            prob_calc(current_goal, rule, queue)
            continue
        
        # inequality
        if rule.predicate == "neq":
            filter_eq(rule, current_goal, queue)
            continue
            
        elif rule.predicate in kb.db:
            ## search relevant buckets so it speeds up search
            rule_f = kb.db[rule.predicate]["facts"]
            if current_goal.parent == None:
                # parent gets query inputs from grandfather to start search
                parent_inherits(rule, rule_f, current_goal, queue)
            else:
                # a child to search facts in kb
                child_assigned(rule, rule_f, current_goal, queue)
    
    answer = answer_handler(answer)
    
    if show_path: 
        path = get_path(kb.db, expr, path)
        return answer, path
    else:
        return answer