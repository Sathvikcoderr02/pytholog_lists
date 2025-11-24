import pytholog as pl

def test_simple_list():
    print("Testing simple list operations")
    
    # Create a knowledge base
    kb = pl.KnowledgeBase("list_test")
    
    # Define a simple list fact
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
    test_simple_list()
