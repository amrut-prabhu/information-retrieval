from collections import defaultdict 

from dictionary import Dictionary
from postingsfile import PostingsFile

def extended_boolean_p_norm_model(query, query_term_weights, document_term_weights):
    """
    http://dns.uls.cl/~ej/daa_08/Algoritmos/books/book5/chap15.htm

    Params:
        - query: boolean query string tokens. Eg. ['"fertility treatment"', 'damages', '"medicine "', 'sick']
        - query_term_weights: Query term weights a_i. { term: query weight }
        - document_term_weights: Document weights for terms d_i. defaultdict of defaultdicts. { docID: { term: doc_term_weight } }
    
    Returns:
        - search_results: Document IDs sorted by relevance [ docID, ... ]
    """
    P = 1 # Operator coefficient p-value to indicate the degree of strictness
    document_values = defaultdict(lambda: {'numerator': 0.0, 'denominator': 0.0})

    for query_token in query:
        for docID, term_weights in document_term_weights.items():
            query_val = pow(query_term_weights[query_token], P)
            doc_term_val = pow(1 - term_weights[query_token], P) # compute numerator value for AND query

            document_values[docID]['numerator'] += query_val * doc_term_val
            document_values[docID]['denominator'] += query_val

    # Compute query-document similarities
    document_similarities = []
    for docID in document_values:
        numer = document_values[docID]['numerator']
        denom = document_values[docID]['denominator']

        similarity = 1 - pow((numer / denom), 1 / P) # compute similarity for AND query
        document_similarities.append((docID, similarity))

    # Sort documents from highest to lowest similarities
    search_results = sorted(document_similarities, key=lambda x: x[1], reverse=True)
    # search_results = [doc[0] for doc in search_results]
    # [(docID, similarity), ...]
    return search_results
