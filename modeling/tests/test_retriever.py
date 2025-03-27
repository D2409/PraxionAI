import sys
import os

# Add the modeling directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
modeling_dir = os.path.abspath(os.path.join(current_dir, "../"))
sys.path.append(modeling_dir)

from retriever import Retriever

def test_retriever():
    retriever = Retriever(index_path="test_index")
    documents = [
        "Policy 1: All data must be encrypted.",
        "Policy 2: Employees must report breaches immediately.",
        "Policy 3: Personal data must not be shared externally."
    ]
    retriever.build_index(documents)
    
    query = "What is the policy on encryption?"
    results, distances = retriever.search(query)

    assert len(results) > 0, "No results found"
    assert "encrypted" in results[0].lower(), "Incorrect retrieval result"
