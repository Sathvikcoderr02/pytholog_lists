import pytholog as pl

print("Testing list implementation in pytholog\n")

# Create a knowledge base
kb = pl.KnowledgeBase("list_test")

# Test 1: Basic list facts
print("Test 1: Basic list facts")
kb(["empty_list([])"])
result = kb.query(pl.Expr("empty_list(X)"))
print(f"empty_list(X) -> {result}")  # Should return [{'X': '[]'}]

# Test 2: List unification
print("\nTest 2: List unification")
kb(["test_list([a,b,c])"])
result = kb.query(pl.Expr("test_list([X,Y,Z])"))
print(f"test_list([X,Y,Z]) -> {result}")  # Should return [{'X': 'a', 'Y': 'b', 'Z': 'c'}]

# Test 3: List membership
print("\nTest 3: List membership")
kb(["member(X, [X|_])."])
kb(["member(X, [_|T]) :- member(X, T)."])
result = kb.query(pl.Expr("member(a, [a,b,c])"))
print(f"member(a, [a,b,c]) -> {result}")  # Should return [{}]

# Test 4: List append
print("\nTest 4: List append")
kb(["append([], L, L)."])
kb(["append([H|T], L2, [H|L3]) :- append(T, L2, L3)."])
result = kb.query(pl.Expr("append([1,2], [3,4], X)"))
print(f"append([1,2], [3,4], X) -> {result}")  # Should return [{'X': '[1,2,3,4]'}]

# Test 5: List length
print("\nTest 5: List length")
kb(["length([], 0)."])
kb(["length([_|T], N) :- length(T, N1), N is N1 + 1."])
result = kb.query(pl.Expr("length([a,b,c,d], N)"))
print(f"length([a,b,c,d], N) -> {result}")  # Should return [{'N': '4'}]
