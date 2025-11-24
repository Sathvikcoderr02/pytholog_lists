import pytholog as pl

def run_minimal_test():
    print("Minimal Test for Empty List")
    
    # Create a knowledge base
    kb = pl.KnowledgeBase("minimal_test")
    
    # Add a simple fact with an empty list
    print("\nAdding fact: empty_list([]).")
    kb(["empty_list([])."])
    
    # Query the knowledge base
    print("Querying: empty_list([])")
    result = kb.query(pl.Expr("empty_list([])"))
    print(f"Result: {result}")
    
    # Print the knowledge base state
    print("\nKnowledge Base State:")
    print(f"Predicates: {kb.db.keys()}")
    if 'empty_list' in kb.db:
        print(f"Facts for 'empty_list': {[f.to_string() for f in kb.db['empty_list']['facts']]}")

if __name__ == "__main__":
    run_minimal_test()
