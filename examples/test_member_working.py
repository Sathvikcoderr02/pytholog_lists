import pytholog as pl

def test_member():
    print("Testing member predicate with various cases")
    
    # Create a knowledge base
    kb = pl.KnowledgeBase("member_test")
    
    # Define the member/2 predicate
    kb(["member(X, [X|_])."])
    kb(["member(X, [_|T]) :- member(X, T)."])
    
    # Test 1: Check if an element is in a list (success case)
    print("\nTest 1: member(a, [a, b, c])")
    result = kb.query(pl.Expr("member(a, [a, b, c])"))
    print(f"Expected: ['Yes'], Got: {result}")
    
    # Test 2: Check if an element is in a list (failure case)
    print("\nTest 2: member(x, [a, b, c])")
    result = kb.query(pl.Expr("member(x, [a, b, c])"))
    print(f"Expected: ['No'], Got: {result}")
    
    # Test 3: Find all elements in a list
    print("\nTest 3: member(X, [a, b, c])")
    result = kb.query(pl.Expr("member(X, [a, b, c])"))
    expected = [{'X': 'a'}, {'X': 'b'}, {'X': 'c'}]
    print(f"Expected: {expected}, Got: {result}")
    
    # Test 4: Nested lists
    print("\nTest 4: member(X, [a, [b, c], d])")
    result = kb.query(pl.Expr("member(X, [a, [b, c], d])"))
    expected = [{'X': 'a'}, {'X': ['b', 'c']}, {'X': 'd'}]
    print(f"Expected: {expected}, Got: {result}")
    
    # Test 5: Member with variables in the list
    print("\nTest 5: member(a, [X, Y, Z])")
    result = kb.query(pl.Expr("member(a, [X, Y, Z])"))
    expected = [{'X': 'a'}, {'Y': 'a'}, {'Z': 'a'}]
    print(f"Expected: {expected}, Got: {result}")

if __name__ == "__main__":
    test_member()
