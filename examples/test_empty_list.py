import pytholog as pl

def test_empty_list():
    print("Testing empty list functionality")
    
    # Create a knowledge base
    kb = pl.KnowledgeBase("empty_list_test")
    
    # Add a fact with an empty list
    print("\nAdding fact: empty_list([]).")
    kb(["empty_list([])."])
    
    # Print the knowledge base state
    print("\nKnowledge Base State:")
    print(f"Predicates: {kb.db.keys()}")
    if 'empty_list' in kb.db:
        print(f"Facts for 'empty_list': {[f.to_string() for f in kb.db['empty_list']['facts']]}")
    
    # Query the knowledge base
    print("\nQuerying: empty_list([])")
    result = kb.query(pl.Expr("empty_list([])"))
    print(f"Result: {result}")
    
    # Expected: ['Yes']
    assert result == ['Yes'], f"Expected ['Yes'], got {result}"
    
    print("\nEmpty list test passed!")

if __name__ == "__main__":
    test_empty_list()
