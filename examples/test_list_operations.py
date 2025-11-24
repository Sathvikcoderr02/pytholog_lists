import pytholog as pl

def run_tests():
    print("Testing List Operations in pytholog\n")
    
    # Create a knowledge base
    kb = pl.KnowledgeBase("list_test")
    
    # Test 1: Empty list
    print("Test 1: Empty list")
    kb(["empty_list([])."])
    result = kb.query(pl.Expr("empty_list([])"))
    print(f"empty_list([]) -> {result}")
    
    # Test 2: List membership
    print("\nTest 2: List membership")
    kb(["member(X, [X|_])."])
    kb(["member(X, [_|T]) :- member(X, T)."])
    
    # Test with specific element
    result = kb.query(pl.Expr("member(b, [a,b,c])"))
    print(f"member(b, [a,b,c]) -> {result}")
    
    # Test with variable
    result = kb.query(pl.Expr("member(X, [a,b,c])"))
    print(f"member(X, [a,b,c]) -> {result}")
    
    # Test 3: List append
    print("\nTest 3: List append")
    kb(["append([], L, L)."])
    kb(["append([H|T], L2, [H|L3]) :- append(T, L2, L3)."])
    
    result = kb.query(pl.Expr("append([1,2], [3,4], X)"))
    print(f"append([1,2], [3,4], X) -> {result}")
    
    # Test 4: List length
    print("\nTest 4: List length")
    kb(["length([], 0)."])
    kb(["length([_|T], N) :- length(T, N1), N is N1 + 1."])
    
    result = kb.query(pl.Expr("length([a,b,c,d], N)"))
    print(f"length([a,b,c,d], N) -> {result}")
    
    # Test 5: List head/tail
    print("\nTest 5: List head/tail")
    kb(["head_tail([H|T], H, T)."])
    
    result = kb.query(pl.Expr("head_tail([1,2,3,4], H, T)"))
    print(f"head_tail([1,2,3,4], H, T) -> {result}")

if __name__ == "__main__":
    run_tests()
