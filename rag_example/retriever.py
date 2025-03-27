from similarity import jaccard_similarity

def retrieve_document(user_input, corpus):
    similarities = [jaccard_similarity(user_input, doc) for doc in corpus]
    max_index = similarities.index(max(similarities))
    return corpus[max_index]
