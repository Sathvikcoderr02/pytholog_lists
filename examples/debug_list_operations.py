import pytholog as pl

def debug_test():
    print("Debugging List Operations in pytholog\n")
    
    # Create a knowledge base
    kb = pl.KnowledgeBase("debug_list_test")
    
    # Test 1: Check how lists are being parsed
    print("Test 1: List Parsing")
    test_terms = [
        "[a,b,c]",
        "[X|Y]",
        "[[a,b],[c,d]]",
        "[1,2,3]"
    ]
    
    for term in test_terms:
        try:
            expr = pl.Expr(term)
            print(f"Term: {term}")
            print(f"  Predicate: {expr.predicate}")
            print(f"  Terms: {expr.terms}")
            print(f"  String: {expr}")
        except Exception as e:
            print(f"Error parsing '{term}': {str(e)}")
    
    # Test 2: Check fact parsing
    print("\nTest 2: Fact Parsing")
    test_facts = [
        "test([a,b,c]).",
        "member(X, [X|_]).",
        "append([], L, L)."
    ]
    
    for fact in test_facts:
        try:
            print(f"\nFact: {fact}")
            f = pl.Fact(fact)
            print(f"  LH: {f.lh}")
            print(f"  LH Terms: {getattr(f.lh, 'terms', 'N/A')}")
            print(f"  RH: {f.rhs}")
        except Exception as e:
            print(f"Error parsing fact '{fact}': {str(e)}")
    
    # Test 3: Simple member test
    print("\nTest 3: Simple Member Test")
    kb(["member(X, [X|_])."])
    kb(["member(X, [_|T]) :- member(X, T)."])
    
    # Print the knowledge base state
    print("\nKnowledge Base State:")
    print(f"Predicates: {kb.db.keys()}")
    if 'member' in kb.db:
        print("Facts for 'member':")
        for fact in kb.db['member']["facts"]:
            print(f"  - {fact}")
    
    # Test query
    print("\nQuery: member(a, [a,b,c])")
    try:
        result = kb.query(pl.Expr("member(a, [a,b,c])"))
        print(f"Result: {result}")
    except Exception as e:
        print(f"Query failed: {str(e)}")
    
    # Test with variable
    print("\nQuery: member(X, [a,b,c])")
    try:
        result = kb.query(pl.Expr("member(X, [a,b,c])"))
        print(f"Result: {result}")
    except Exception as e:
        print(f"Query failed: {str(e)}")

if __name__ == "__main__":
    debug_test()
