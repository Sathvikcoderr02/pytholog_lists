import pytholog as pl

def test_list_parsing():
    print("Testing list parsing...")
    
    # Test basic list parsing
    kb = pl.KnowledgeBase("list_test")
    
    # Test 1: Empty list
    print("\nTest 1: Empty list")
    empty_list = pl.Expr("[]")
    print(f"Empty list: {empty_list.terms if hasattr(empty_list, 'terms') else empty_list}")
    
    # Test 2: Simple list
    print("\nTest 2: Simple list")
    simple_list = pl.Expr("[a, b, c]")
    print(f"Simple list: {simple_list.terms if hasattr(simple_list, 'terms') else simple_list}")
    
    # Test 3: List with variables
    print("\nTest 3: List with variables")
    var_list = pl.Expr("[X, Y, Z]")
    print(f"List with variables: {var_list.terms if hasattr(var_list, 'terms') else var_list}")
    
    # Test 4: List pattern [H|T]
    print("\nTest 4: List pattern [H|T]")
    pattern = pl.Expr("[H|T]")
    print(f"List pattern: {pattern.terms if hasattr(pattern, 'terms') else pattern}")
    
    # Test 5: List pattern with anonymous variable
    print("\nTest 5: List pattern with anonymous variable")
    anon_pattern = pl.Expr("[H|_]")
    print(f"List pattern with _: {anon_pattern.terms if hasattr(anon_pattern, 'terms') else anon_pattern}")

def test_member_predicate():
    print("\nTesting member predicate...")
    
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
    test_list_parsing()
    test_member_predicate()
