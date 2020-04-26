from collections import defaultdict
import nltk
import os
import math
from math import sqrt
import heapq
import string
import sys

import util

def eval_free_text_query(query_tokens, dictionary, postings_file, is_boolean=False, is_rocchio=False):
    """
    Performs search for free text query using tf-idf scoring. 
    Evaluates the query and returns ranked results based on lnc.ltc
    
    :param query_tokens: list of query terms with term weights. [ (term, weight), ...]
    :param dictionary: Object of Dictionary
    :param postings_file: Object of PostingsFile
    :param is_boolean: Whether this query is for a boolean query
    
    :return: 
        - If it is free text query, uses `document_score` for list of 
        ranked results. [ docID, ... ]

        - If it is boolean query, returns `doc_scores` with ranked results and 
        normalised scores. [ (docID, score), ... ]
    """
    tf_query = defaultdict(int)
    document_score = defaultdict(float)
    query_norm_tokens = list()
    total_docs = dictionary.get_doc_count()

    if is_rocchio:
        tf_query = query_tokens
        query_norm_tokens = list(query_tokens.keys())
    else:
        for token, weight in query_tokens:
            query_norm_tokens.append(token)
            tf_query[token] += 1 * weight

    norm_query = 0
    for norm_token in set(query_norm_tokens):
        offset, size = dictionary.get_offset_and_size_of_term(norm_token)

        if offset != -1:
            posting_list = postings_file.get_posting_list(offset, size, dictionary) 
        else:  
            # For unknown words, skip updates
            continue

        df = dictionary.get_df(norm_token)

        if df == 0 or df == -1:
            idf = 0
        else:
            idf = util.log10(total_docs / df)

        wt = idf * (1 + util.log10(tf_query[norm_token]))
        norm_query += (wt * wt)

        # Update document tf-idf scores
        for posting in posting_list:
            doc_id = posting[0]
            tf_doc = posting[1]
            doc_norm_len = dictionary.get_normalised_doc_length(str(doc_id))

            document_score[doc_id] += wt * (tf_doc / doc_norm_len)

    norm_query = sqrt(norm_query) # Length of query vector

    scores = []
    docIds = []
    for docId, score in document_score.items():
        document_score[docId] = score / norm_query

        docIds.append(docId)
        scores.append(score / norm_query)

    if not is_boolean:
        # Return ranked documents for free text query
        return heapq.nlargest(len(document_score), document_score, key=document_score.__getitem__)


    # Normalise scores using softmax
    exp_scores = []
    for s in scores:
        exp_scores.append(math.exp(s))
    sum_exp_scores = sum(exp_scores)

    doc_scores = []
    for i, s in enumerate(exp_scores):
        score = s / sum_exp_scores
        doc_scores.append((docIds[i], score))
    
    doc_scores = sorted(doc_scores, key=lambda x: x[1])

    return doc_scores
