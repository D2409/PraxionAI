import os
import numpy as np
import torch
from sentence_transformers import SentenceTransformer, util

# Load the sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load the corpus from corpus.py
from corpus import corpus_of_documents

# Precompute embeddings once during app start
corpus_embeddings = model.encode(corpus_of_documents, convert_to_tensor=True)

def get_response(user_query, top_k=1):
    """
    Takes a user query, finds the most similar sentence(s) in the corpus,
    and returns the most relevant response.
    """
    query_embedding = model.encode(user_query, convert_to_tensor=True)

    # Compute cosine similarity between the query and the corpus
    hits = util.semantic_search(query_embedding, corpus_embeddings, top_k=top_k)
    hits = hits[0]  # Only one query at a time

    # Get the top result
    top_match = hits[0]
    best_index = top_match['corpus_id']
    best_score = top_match['score']

    best_sentence = corpus_of_documents[best_index]

    
    print("\n🔍 User Query:", user_query)
    print("🔍 Top Match:", best_sentence)
    print("🔍 Similarity Score:", best_score)

    # Add confidence threshold (e.g., 0.6)
    """ 
    if best_score < 0.6:
        return "Sorry, I couldn't find a relevant answer." """

    


    # Optional: Add a confidence check or formatting
    return best_sentence