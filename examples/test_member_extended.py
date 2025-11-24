from pytholog import KnowledgeBase, Expr

def test_extended_member():
    print("Testing extended member/2 predicate...\n")
    
    # Create a new knowledge base
    kb = KnowledgeBase()
    
    # Add member predicate rules
    kb.add_kn(["member(X, [X|_])."])
    kb.add_kn(["member(X, [_|T]) :- member(X, T)."])
    
    # Test 1: Check multiple elements in a list
    test_cases = [
        ("member(a, [a, b, c])", ["Yes"], "Element at start"),
        ("member(b, [a, b, c])", ["Yes"], "Element in middle"),
        ("member(c, [a, b, c])", ["Yes"], "Element at end"),
        ("member(d, [a, b, c])", ["No"], "Element not in list"),
        ("member([b], [a, [b], c])", ["Yes"], "List as element"),
        ("member(X, [a, b, c])", [{"X": "a"}], "Find first element"),
        ("member(X, [])", ["No"], "Empty list"),
        ("member(X, [a])", [{"X": "a"}], "Single element list"),
        ("member(a, [X, b, c])", ["Yes"], "Variable in list"),
        ("member(X, [a, b, a])", [{"X": "a"}], "Duplicate elements")
    ]
    
    for query, expected, description in test_cases:
        print(f"\nTest: {description}")
        print(f"Query: {query}")
        result = kb.query(Expr(query))
        print(f"Expected: {expected}")
        print(f"Got: {result}")
        
        # For variable queries, check if we got at least one solution
        if 'X' in query and expected and isinstance(expected[0], dict):
            assert len(result) > 0 and isinstance(result[0], dict), \
                f"Failed {description}: Expected at least one solution"
        else:
            assert result == expected, f"Failed {description}"
    
    print("\nAll extended tests passed!")

if __name__ == "__main__":
    test_extended_member()
