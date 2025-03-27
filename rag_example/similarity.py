def jaccard_similarity(query, document):
    query_set = set(query.lower().split())
    document_set = set(document.lower().split())
    intersection = query_set.intersection(document_set)
    union = query_set.union(document_set)
    return len(intersection) / len(union)
