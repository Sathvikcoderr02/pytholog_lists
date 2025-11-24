from pytholog import KnowledgeBase, Expr

def test_subset():
    print("Testing subset/2 predicate...\n")
    
    # Create a new knowledge base
    kb = KnowledgeBase("test_subset")
    
    # Define the subset predicate rules
    kb([
        "subset([], _).",  # Base case: empty list is a subset of any list
        "subset([H|T], List) :- member(H, List), subset(T, List)."  # Recursive case
    ])
    
    # Test 1: Check if [a, b] is a subset of [a, b, c]
    print("Test 1: subset([a, b], [a, b, c])")
    result1 = kb.query(Expr("subset([a, b], [a, b, c])"))
    print(f"Expected: ['Yes'], Got: {result1}")
    
    # Test 2: Check if [a, x] is a subset of [a, b, c] (should be No)
    print("\nTest 2: subset([a, x], [a, b, c])")
    result2 = kb.query(Expr("subset([a, x], [a, b, c])"))
    print(f"Expected: ['No'], Got: {result2}")
    
    # Test 3: Check if [] is a subset of any list
    print("\nTest 3: subset([], [a, b, c])")
    result3 = kb.query(Expr("subset([], [a, b, c])"))
    print(f"Expected: ['Yes'], Got: {result3}")
    
    # Test 4: Find all subsets of [a, b, c]
    print("\nTest 4: subset(X, [a, b, c])")
    result4 = kb.query(Expr("subset(X, [a, b, c])"))
    print(f"Got: {result4}")

if __name__ == "__main__":
    test_subset()
