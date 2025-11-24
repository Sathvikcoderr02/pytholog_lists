from pytholog import KnowledgeBase, Expr

def debug_member():
    print("Debugging member/2 predicate with direct list handling...\n")
    
    # Create a new knowledge base
    kb = KnowledgeBase("debug_member")
    
    # Directly test list handling without relying on the knowledge base
    def test_member(element, lst):
        print(f"\nTesting member({element}, {lst})")
        
        # Helper function to check if a term is a variable
        def is_variable(term):
            return isinstance(term, str) and (term[0].isupper() or term.startswith('_'))
        
        # Helper function to parse list strings
        def parse_list(lst_str):
            if isinstance(lst_str, list):
                return lst_str
            if isinstance(lst_str, str) and lst_str.startswith('[') and lst_str.endswith(']'):
                try:
                    if '|' in lst_str:
                        # Handle [H|T] format
                        inner = lst_str[1:-1].strip()
                        head, tail = inner.split('|', 1)
                        return [head.strip(), '|', tail.strip()]
                    else:
                        # Handle [a,b,c] format
                        items = [item.strip() for item in lst_str[1:-1].split(',') if item.strip()]
                        return items if len(items) > 1 else (items[0] if items else [])
                except Exception as e:
                    print(f"[DEBUG] Error parsing list string: {e}")
            return lst_str
        
        # Parse the list if it's a string
        parsed_lst = parse_list(lst)
        if parsed_lst is not None and parsed_lst != lst:
            lst = parsed_lst
        
        # Custom member implementation
        def member_impl(elem, l):
            print(f"[DEBUG] member_impl({elem}, {l}) (type: {type(l)})")
            
            # If the element is a variable, find all possible values
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
            
            # Check if element is in the list
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
        
        # Test with our implementation
        return member_impl(element, lst)
    
    # Test cases
    print("Test 1: member(a, [a, b, c])")
    result1 = test_member('a', '[a, b, c]')
    print(f"Result: {result1} (Expected: ['Yes'])")
    
    print("\nTest 2: member(b, [a, b, c])")
    result2 = test_member('b', '[a, b, c]')
    print(f"Result: {result2} (Expected: ['Yes'])")
    
    print("\nTest 3: member(x, [a, b, c])")
    result3 = test_member('x', '[a, b, c]')
    print(f"Result: {result3} (Expected: ['No'])")
    
    print("\nTest 4: member(X, [a, b, c])")
    result4 = test_member('X', '[a, b, c]')
    expected = [{'X': 'a'}, {'X': 'b'}, {'X': 'c'}]
    print(f"Result: {result4} (Expected: {expected})")
    
    print("\nDebugging completed!")

if __name__ == "__main__":
    debug_member()
