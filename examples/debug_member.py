import pytholog as pl

def test_member_basic():
    print("Testing basic member functionality")
    
    # Create a knowledge base
    kb = pl.KnowledgeBase("member_test")
    
    # Add the member predicate
    print("\nAdding member facts...")
    kb(["member(X, [X|_])."])
    kb(["member(X, [_|T]) :- member(X, T)."])
    
    # Test 1: Simple member check
    print("\nTest 1: member(a, [a, b, c])")
    result = kb.query(pl.Expr("member(a, [a, b, c])"))
    print(f"Result: {result}")
    
    # Test 2: Variable binding
    print("\nTest 2: member(X, [a, b, c])")
    result = kb.query(pl.Expr("member(X, [a, b, c])"))
    print(f"Result: {result}")
    
    # Test 3: Non-member check
    print("\nTest 3: member(x, [a, b, c])")
    result = kb.query(pl.Expr("member(x, [a, b, c])"))
    print(f"Result: {result}")

if __name__ == "__main__":
    test_member_basic()
