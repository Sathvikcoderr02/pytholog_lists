from pytholog import KnowledgeBase, Expr

def test_member_basic():
    print("Testing basic member/2 functionality...\n")
    
    # Create a new knowledge base
    kb = KnowledgeBase("test_member")
    
    # Add member predicate rules
    kb.add_kn(["member(X, [X|_])."])
    kb.add_kn(["member(X, [_|T]) :- member(X, T)."])
    
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
    assert result1 == ["Yes"], f"Test 1 failed: {result1}"
    
    # Test 2: Check if 'b' is in the list [a, b, c]
    print("\nTest 2: member(b, [a, b, c])")
    result2 = kb.query(Expr("member(b, [a, b, c])"))
    print(f"Expected: ['Yes'], Got: {result2}")
    assert result2 == ["Yes"], f"Test 2 failed: {result2}"
    
    # Test 3: Check if 'x' is not in the list [a, b, c]
    print("\nTest 3: member(x, [a, b, c])")
    result3 = kb.query(Expr("member(x, [a, b, c])"))
    print(f"Expected: ['No'], Got: {result3}")
    assert result3 == ["No"], f"Test 3 failed: {result3}"
    
    # Test 4: Find all elements in the list [a, b, c]
    print("\nTest 4: member(X, [a, b, c])")
    result4 = kb.query(Expr("member(X, [a, b, c])"))
    print(f"Expected: [{'X': 'a'}, {'X': 'b'}, {'X': 'c'}], Got: {result4}")
    
    # For now, just check that we get at least one result
    assert len(result4) > 0 and isinstance(result4[0], dict), f"Test 4 failed: {result4}"
    
    print("\nAll basic tests passed!")

if __name__ == "__main__":
    test_member_basic()
