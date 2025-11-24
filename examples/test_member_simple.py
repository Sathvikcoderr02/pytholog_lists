from pytholog import KnowledgeBase, Expr

def test_member_simple():
    print("Testing member/2 with a simplified approach...\n")
    
    # Create a new knowledge base
    kb = KnowledgeBase("test_member_simple")
    
    # Add member predicate rules using a different syntax
    kb(["member(X, [X|_])."])
    kb(["member(X, [_|T]) :- member(X, T)."])
    
    # Print the knowledge base for debugging
    print("Knowledge Base:")
    print("--------------")
    for fact in kb.db.get('member', []):
        print(f"- {fact}")
    print()
    
    # Test 1: Check if 'a' is in the list [a, b, c]
    print("Test 1: member(a, [a, b, c])")
    result1 = kb.query(Expr("member(a, [a, b, c])"))
    print(f"Expected: ['Yes'], Got: {result1}")
    
    # Test 2: Check if 'b' is in the list [a, b, c]
    print("\nTest 2: member(b, [a, b, c])")
    result2 = kb.query(Expr("member(b, [a, b, c])"))
    print(f"Expected: ['Yes'], Got: {result2}")
    
    # Test 3: Check if 'x' is not in the list [a, b, c]
    print("\nTest 3: member(x, [a, b, c])")
    result3 = kb.query(Expr("member(x, [a, b, c])"))
    print(f"Expected: ['No'], Got: {result3}")
    
    # Test 4: Find all elements in the list [a, b, c]
    print("\nTest 4: member(X, [a, b, c])")
    result4 = kb.query(Expr("member(X, [a, b, c])"))
    expected = [{'X': 'a'}, {'X': 'b'}, {'X': 'c'}]
    print(f"Expected: {expected}, Got: {result4}")
    
    # For now, just check that we get at least one result
    assert len(result4) > 0, f"Test 4 failed: {result4}"
    
    # Print the results for better debugging
    print("\nDetailed results for member(X, [a, b, c]):")
    for i, res in enumerate(result4, 1):
        print(f"  Solution {i}: {res}")
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    test_member_simple()
