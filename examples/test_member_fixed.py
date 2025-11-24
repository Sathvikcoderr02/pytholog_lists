import pytholog as pl

def test_member():
    print("Testing member predicate with improved unification")
    
    # Create a knowledge base
    kb = pl.KnowledgeBase("member_test")
    
    # Define the member/2 predicate
    kb(["member(X, [X|_])."])
    kb(["member(X, [_|T]) :- member(X, T)."])
    
    # Test 1: Check if an element is in a list
    print("\nTest 1: member(a, [a, b, c])")
    result = kb.query(pl.Expr("member(a, [a, b, c])"))
    print(f"Result: {result}")
    
    # Test 2: Find all elements in a list
    print("\nTest 2: member(X, [a, b, c])")
    result = kb.query(pl.Expr("member(X, [a, b, c])"))
    print(f"Result: {result}")
    
    # Test 3: Check with a non-existent element
    print("\nTest 3: member(x, [a, b, c])")
    result = kb.query(pl.Expr("member(x, [a, b, c])"))
    print(f"Result: {result}")
    
    # Test 4: Nested lists
    print("\nTest 4: member(X, [a, [b, c], d])")
    result = kb.query(pl.Expr("member(X, [a, [b, c], d])"))
    print(f"Result: {result}")
    
    # Test 5: Member with variables in the list
    print("\nTest 5: member(a, [X, Y, Z])")
    result = kb.query(pl.Expr("member(a, [X, Y, Z])"))
    print(f"Result: {result}")

if __name__ == "__main__":
    test_member()
