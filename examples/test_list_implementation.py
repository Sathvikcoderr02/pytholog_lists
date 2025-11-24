import pytholog as pl

def test_list_implementation():
    print("Testing List Implementation in pytholog\n")
    
    # Create a knowledge base
    kb = pl.KnowledgeBase("list_tests")
    
    # Test 1: Empty list
    print("Test 1: Empty list")
    kb(["empty_list([])."])
    result = kb.query(pl.Expr("empty_list([])"))
    print(f"empty_list([]) -> {result}")  # Should return ['Yes']
    
    # Test 2: List membership
    print("\nTest 2: List membership")
    kb(["member(X, [X|_])."])
    kb(["member(X, [_|T]) :- member(X, T)."])
    
    # Test with specific element
    result = kb.query(pl.Expr("member(b, [a,b,c])"))
    print(f"member(b, [a,b,c]) -> {result}")  # Should return ['Yes']
    
    # Test with variable
    result = kb.query(pl.Expr("member(X, [a,b,c])"))
    print(f"member(X, [a,b,c]) -> {result}")  # Should return bindings for X
    
    # Test 3: List append
    print("\nTest 3: List append")
    kb(["append([], L, L)."])
    kb(["append([H|T], L2, [H|L3]) :- append(T, L2, L3)."])
    
    result = kb.query(pl.Expr("append([1,2], [3,4], X)"))
    print(f"append([1,2], [3,4], X) -> {result}")  # Should show X = [1,2,3,4]
    
    # Test 4: List length
    print("\nTest 4: List length")
    kb(["length([], 0)."])
    kb(["length([_|T], N) :- length(T, N1), N is N1 + 1."])
    
    result = kb.query(pl.Expr("length([a,b,c,d], N)"))
    print(f"length([a,b,c,d], N) -> {result}")  # Should show N = 4
    
    # Test 5: List head/tail
    print("\nTest 5: List head/tail")
    result = kb.query(pl.Expr("member(Head, [a,b,c]), member(Tail, [[b,c], [c], []]), append([Head], Tail, [a,b,c])"))
    print(f"List decomposition -> {result}")  # Should show valid decompositions

if __name__ == "__main__":
    test_list_implementation()
