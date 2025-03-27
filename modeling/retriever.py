from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os

class Retriever:
    def __init__(self, index_path="faiss_index"):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")  # Pre-trained embedding model
        self.index_path = index_path
        self.index = None
        self.documents = []  # Store original documents

        # Load existing index if it exists
        if os.path.exists(index_path):
            self.load_index()

    def build_index(self, documents):
        """Build FAISS index from a list of documents."""
        self.documents = documents
        embeddings = self.model.encode(documents, convert_to_numpy=True)
        self.index = faiss.IndexFlatL2(embeddings.shape[1])  # L2 distance metric
        self.index.add(embeddings)
        self.save_index()

    def save_index(self):
        """Save FAISS index to a file."""
        faiss.write_index(self.index, self.index_path)

    def load_index(self):
        """Load FAISS index from a file."""
        self.index = faiss.read_index(self.index_path)

    def search(self, query, top_k=5):
        """Search the FAISS index for the most relevant documents."""
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        distances, indices = self.index.search(query_embedding, top_k)
        results = [self.documents[i] for i in indices[0]]
        return results, distances[0]
