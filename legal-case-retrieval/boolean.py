import sys
import getopt
import util
import linecache
import math
from collections import defaultdict
from spellchecker import SpellChecker
import heapq

from nltk.corpus import wordnet
from nltk.wsd import lesk

from dictionary import Dictionary
from postingsfile import PostingsFile
from extended_boolean import extended_boolean_p_norm_model
import tf_idf
import query_expansion

def retrieve_query_term_postings(query_term, dictionary, postings_file, should_get_positions=False):
    """
    Gets the postings list for the query term from the disk.

    Params:
        - query_term: term to retrive postings for
        - dictionary: Dictionary object
        - postings_file: PostingsFile object
        - should_get_positions: Whether positional index is required

    Returns:
        - postings: [ (docID, log-tf), ... ] or [ (docID, [position, ...], log-tf), ... ]
    """
    query_term = util.preprocess_content(query_term)[0]

    offset, size = dictionary.get_offset_and_size_of_term(query_term)

    if offset != -1:
        if should_get_positions:
            term_postings = postings_file.get_posting_list_with_positions(offset, size, dictionary)
        else:
            term_postings = postings_file.get_posting_list(offset, size, dictionary)
    else:
        term_postings = []

    return term_postings


def retrieve_phrasal_query_postings(query_str, dictionary, postings_file):
    """
    Retrieves the postings lists for the phrasal query from the disk.
    Performs positional intersect to get the postings list.

    Params:
        - query_str: Phrasal query term. Eg. fertility treatment
        - dictionary: Dictionary object
        - postings_file: PostingsFile object

    Returns:
        postings: [ (docID, log-tf), ...  ]
    """
    query_terms = [query_term.strip() for query_term in query_str.split(' ')]
    phrasal_query_size = len(query_terms)

    postings_lists = []
    for query_term in query_terms:
        term_postings = retrieve_query_term_postings(query_term, dictionary, postings_file, True)
        postings_lists.append(term_postings)

    phrasal_query_postings = util.positional_intersect(phrasal_query_size == 2, *postings_lists)

    return phrasal_query_postings


def eval_boolean_query(query, dictionary, postings_file):
    """
    Params:
        - query: boolean query string tokens. Eg. ['"fertility treatment"', 'damages', '"medicine "', 'sick']
        - dictionary: Dictionary object
        - postings_file: PostingsFile object

    Returns:
        search_results: [ (docID, log-tf), ... ]
    """
    query_postings = []  # [ [ (docID, log-tf), ... ], ... ]

    for query_term in query:
        postings = None

        if query_term[0] == '"' and query_term[-1] == '"':
            postings = retrieve_phrasal_query_postings(query_term[1:-1], dictionary, postings_file)
        else:
            postings = retrieve_query_term_postings(query_term, dictionary, postings_file)

        query_postings.append(postings)

    query_postings_lengths = [(idx, len(postings)) for idx, postings in enumerate(query_postings)]
    query_postings_lengths = sorted(query_postings_lengths, key=lambda x: x[1])

    search_results = query_postings[query_postings_lengths[0][0]]

    for i in range(1, len(query_postings_lengths)):
        postings = query_postings[query_postings_lengths[i][0]]

        search_results = util.perform_and_operation(search_results, postings)

    # search_results = [doc[0] for doc in search_results]
    # return search_results

    docIds = []
    scores = []
    for docId, log_tf in search_results:
        docIds.append(docId)
        scores.append(log_tf)


    s = []
    for x in scores:
        s.append(math.exp(x))

    y = sum(s)
    scores = []
    for x in s:
        scores.append(x / y)

    docs = []
    for i in range(len(docIds)):
        docs.append((docIds[i], scores[i]))
    
    docs = sorted(docs, key=lambda x: x[1])

    return docs


def eval_extended_boolean_query(query, dictionary, postings_file):
    """
      Params:
        - query: boolean query string tokens. Eg. ['"fertility treatment"', 'damages', '"medicine "', 'sick']
        - dictionary: Dictionary object
        - postings_file: PostingsFile object

      Returns:
        - search_results: [ (docID, log-tf), ... ]
    """
    DEFAULT_QUERY_TERM_WT = 1  # uniform term importance weights. Eg. 1 or assign based on idf

    query_term_weights = {}  # { term: query weight }
    document_term_weights = defaultdict(lambda: defaultdict(lambda: 0.0))  # { docID: { term: lnc tf-idf weight } }

    total_docs = dictionary.get_doc_count()

    for query_token in set(query):
        df = dictionary.get_df(util.preprocess_content(query_token)[0])
        if df == 0 or df == -1:
            idf = 0.001
        else:
            idf = util.log10(total_docs / df)

        query_term_weights[query_token] = idf  # DEFAULT_QUERY_TERM_WT

        postings = None
        if query_token[0] == '"' and query_token[-1] == '"':
            postings = retrieve_phrasal_query_postings(query_token[1:-1], dictionary, postings_file)
        else:
            postings = retrieve_query_term_postings(query_token, dictionary, postings_file)

        for (docId, log_tf) in postings:
            doc_len = dictionary.get_normalised_doc_length(str(docId))
            document_term_weights[docId][query_token] = log_tf / doc_len

    return extended_boolean_p_norm_model(query, query_term_weights, document_term_weights)


def rank_results_bool(results_bool, results_ex_bool, results_lnc):
    """
    Rank the results using weighted sum of normalised log-tf, p-norm, and tf-idf scores
    from the inputs.

    Params:
        - results_bool, results_ex_bool, results_lnc: [ (docID, score), ...]
    """
    document_scores = defaultdict(lambda: 0)

    LOG_TF_WEIGHT = 0.5
    P_NORM_WEIGHT = 0.85
    TF_IDF_WEIGHT = 0.7

    for docId, val in results_bool:
        document_scores[docId] += LOG_TF_WEIGHT * val

    for docId, val in results_ex_bool:
        document_scores[docId] += P_NORM_WEIGHT * val

    for docId, val in results_lnc:
        document_scores[docId] += TF_IDF_WEIGHT * val

    return heapq.nlargest(len(document_scores), document_scores, key=document_scores.__getitem__)
