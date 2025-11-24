import pytholog as pl

def test_list_parsing():
    print("\n=== Testing List Parsing ===")
    
    # Test 1: Simple list
    expr = pl.Expr("[a, b, c]")
    print(f"\nTest 1: {expr}")
    print(f"Predicate: {expr.predicate}")
    print(f"Terms: {getattr(expr, 'terms', 'N/A')}")
    
    # Test 2: List with variables
    expr = pl.Expr("[X, Y, Z]")
    print(f"\nTest 2: {expr}")
    print(f"Predicate: {expr.predicate}")
    print(f"Terms: {getattr(expr, 'terms', 'N/A')}")
    
    # Test 3: Empty list
    expr = pl.Expr("[]")
    print(f"\nTest 3: {expr}")
    print(f"Predicate: {expr.predicate}")
    print(f"Terms: {getattr(expr, 'terms', 'N/A')}")

def test_member_predicate():
    print("\n=== Testing Member Predicate ===")
    
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

def test_list_facts():
    print("\n=== Testing List Facts ===")
    
    # Create a knowledge base
    kb = pl.KnowledgeBase("list_facts")
    
    # Define a list fact
    kb(["colors([red, green, blue])."])
    
    # Test 1: Query the list
    print("\nTest 1: colors(X)")
    result = kb.query(pl.Expr("colors(X)"))
    print(f"Result: {result}")
    
    # Test 2: Check if red is in the list
    print("\nTest 2: member(red, [red, green, blue])")
    result = kb.query(pl.Expr("member(red, [red, green, blue])"))
    print(f"Result: {result}")
    
    # Test 3: Find all elements in the list
    print("\nTest 3: member(X, [red, green, blue])")
    result = kb.query(pl.Expr("member(X, [red, green, blue])"))
    print(f"Result: {result}")

if __name__ == "__main__":
    test_list_parsing()
    test_member_predicate()
    test_list_facts()
