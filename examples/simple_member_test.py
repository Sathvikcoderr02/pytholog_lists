import pytholog as pl

def test_simple_member():
    print("Testing simple member predicate")
    
    # Create a knowledge base
    kb = pl.KnowledgeBase("simple_member_test")
    
    # Add some test facts
    kb(["likes(john, mary)."])
    kb(["likes(mary, pizza)."])
    kb(["likes(mary, wine)."])
    
    # Test 1: Simple fact query
    print("\nTest 1: likes(john, mary)")
    result = kb.query(pl.Expr("likes(john, mary)"))
    print(f"Result: {result}")
    
    # Test 2: Simple fact query with variable
    print("\nTest 2: likes(mary, X)")
    result = kb.query(pl.Expr("likes(mary, X)"))
    print(f"Result: {result}")
    
    # Test 3: Member with hardcoded list
    print("\nTest 3: member(a, [a, b, c])")
    # Directly test the list parsing and member functionality
    from pytholog.expr import Expr
    
    # Test list parsing
    test_list = "[a, b, c]"
    parsed = Expr(test_list)
    print(f"Parsed list: {parsed}")
    if hasattr(parsed, 'terms'):
        print(f"List terms: {parsed.terms}")
    
    # Test member functionality
    def simple_member(X, L):
        if not L:
            return False
        if X == L[0]:
            return True
        return simple_member(X, L[1:])
    
    test_list = ['a', 'b', 'c']
    print(f"Testing simple_member('a', {test_list}): {simple_member('a', test_list)}")
    print(f"Testing simple_member('x', {test_list}): {simple_member('x', test_list)}")
    
    # Try to add a member fact and query it
    print("\nAdding member fact...")
    kb(["member(X, [X|_])."])
    print("Current facts:", kb.db.get('member', {}).get('facts', []))
    
    print("\nQuerying member(a, [a, b, c])")
    result = kb.query(pl.Expr("member(a, [a, b, c])"))
    print(f"Result: {result}")

if __name__ == "__main__":
    test_simple_member()
