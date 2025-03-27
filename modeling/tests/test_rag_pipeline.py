from rag_pipeline import RAGPipeline

def test_rag_pipeline():
    rag = RAGPipeline()
    documents = ["Policy 1: All data must be encrypted.", "Policy 2: Employees must report breaches."]
    question = "What is the encryption policy?"
    
    answer = rag.answer_question(question, documents)
    assert "encrypted" in answer, "RAG failed to generate the correct answer."
