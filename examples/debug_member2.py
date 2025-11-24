from pytholog import KnowledgeBase, Expr

def debug_member():
    print("Debugging member/2 predicate...\n")
    
    # Create a new knowledge base
    kb = KnowledgeBase("debug_member")
    
    # Add member predicate rules using a different syntax
    print("Adding member/2 rules...")
    kb(["member(X, [X|_])."])
    kb(["member(X, [_|T]) :- member(X, T)."])
    
    # Print the knowledge base for debugging
    print("\nKnowledge Base:")
    print("--------------")
    for fact in kb.db.get('member', []):
        print(f"- {fact}")
    
    # Test 1: Check if 'a' is in the list [a, b, c]
    print("\nTest 1: member(a, [a, b, c])")
    query1 = Expr("member(a, [a, b, c])")
    print(f"Query: {query1}")
    result1 = kb.query(query1)
    print(f"Result: {result1}")
    print(f"Expected: ['Yes'], Got: {result1}")
    
    # Test 2: Check if 'b' is in the list [a, b, c]
    print("\nTest 2: member(b, [a, b, c])")
    query2 = Expr("member(b, [a, b, c])")
    print(f"Query: {query2}")
    result2 = kb.query(query2)
    print(f"Result: {result2}")
    print(f"Expected: ['Yes'], Got: {result2}")
    
    # Test 3: Check if 'x' is not in the list [a, b, c]
    print("\nTest 3: member(x, [a, b, c])")
    query3 = Expr("member(x, [a, b, c])")
    print(f"Query: {query3}")
    result3 = kb.query(query3)
    print(f"Result: {result3}")
    print(f"Expected: ['No'], Got: {result3}")
    
    # Test 4: Find all elements in the list [a, b, c]
    print("\nTest 4: member(X, [a, b, c])")
    query4 = Expr("member(X, [a, b, c])")
    print(f"Query: {query4}")
    result4 = kb.query(query4)
    print(f"Result: {result4}")
    expected = [{'X': 'a'}, {'X': 'b'}, {'X': 'c'}]
    print(f"Expected: {expected}, Got: {result4}")
    
    # Print the results for better debugging
    print("\nDetailed results for member(X, [a, b, c]):")
    for i, res in enumerate(result4, 1):
        print(f"  Solution {i}: {res}")
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    debug_member()
