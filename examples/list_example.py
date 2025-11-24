import pytholog as pl

# Create a knowledge base
kb = pl.KnowledgeBase("list_example")

# Define some facts with lists
kb([
    "empty_list([])",
    "list_head_tail([H|T], H, T)",
    "list_member(X, [X|_]) :- !",
    "list_member(X, [_|T]) :- list_member(X, T)",
    "list_append([], L, L).",
    "list_append([H|T], L2, [H|L3]) :- list_append(T, L2, L3).",
    "list_length([], 0).",
    "list_length([_|T], N) :- list_length(T, N1), N is N1 + 1"
])

# Test empty list
print("Testing empty list:")
print(kb.query(pl.Expr("empty_list([])")))  # Should return ['Yes']

# Test list head/tail
print("\nTesting list head/tail:")
print(kb.query(pl.Expr("list_head_tail([a,b,c], H, T)")))  # Should return [{'H': 'a', 'T': '[b,c]'}]

# Test list membership
print("\nTesting list membership:")
print(kb.query(pl.Expr("list_member(b, [a,b,c])")))  # Should return [{}]
print(kb.query(pl.Expr("list_member(X, [a,b,c])")))  # Should return [{'X': 'a'}, {'X': 'b'}, {'X': 'c'}]

# Test list append
print("\nTesting list append:")
print(kb.query(pl.Expr("list_append([a,b], [c,d], X)")))  # Should return [{'X': '[a,b,c,d]'}]

# Test list length
print("\nTesting list length:")
print(kb.query(pl.Expr("list_length([a,b,c,d], N)")))  # Should return [{'N': '4'}]
