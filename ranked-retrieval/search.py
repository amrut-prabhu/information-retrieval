#!/usr/bin/python3
import re
import nltk
import sys
import getopt

import linecache
import _pickle as pickle
import math
import heapq

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")


def log10(x):
    """
    Returns log base 10 for positive input, and zero otherwise.
    """
    if x > 0:
        return math.log(x, 10)
    
    return 0


def read_postings_list_from_disk(offset, postings_fo):
    """
    Returns the postings list of the `word`, read from the postings file.
    
    Input:
        offset: Position to start reading from in the file
        postings_fo: File containing the postings lists

    Output:
        Postings list of document IDs and normalised term frequency 
        weights [ (doc_id, n_wt), ... ]
    """
    postings_fo.seek(offset, 0)
    postings = pickle.load(postings_fo)

    return postings


def calculate_document_scores(query_tfs, dictionary, postings_fo):
    """
    Returns the postings list of the `word`, read from the postings file.
    
    Input:
        query_tfs: Raw term frequency counts for the query { word_type: tf }
        dictionary: { word_type : (idf, offset_bytes) } 
        postings_fo: File containing the postings lists

    Output:
        Dict with scores assigned to documents relevant to the 
        query { doc_id: score }
    """
    doc_scores = {}

    for term in query_tfs:
        if term not in dictionary:
            continue

        # No need to normalize query weights since it is shared between all 
        # document scores, and we just want relative scores
        (idf, offset) = dictionary[term]
        wt_tq = (1 + log10(query_tfs[term])) * idf 

        postings = read_postings_list_from_disk(offset, postings_fo)
        for (doc_id, n_wt_td) in postings:
            if doc_id not in doc_scores:
                doc_scores[doc_id] = 0
            doc_scores[doc_id] += n_wt_td * wt_tq

    return doc_scores


def perform_search_query(query, dictionary, postings_fo):
    """
    Returns list of top ranked documents (up to K=10), sorted by decreasing 
    relevance, and increasing doc ID.
    Query terms are processed using stemming and case folding.

    Input:
        query: String of query terms

    Output:
        List of doc IDs, with maximum size of 10
    """
    K = 10

    query_tfs = {}

    stemmer = nltk.stem.porter.PorterStemmer()
    tokens = nltk.word_tokenize(query)
    for token in tokens:
        # Apply stemming and case folding as done during indexing
        term = stemmer.stem(token).lower()

        if term not in query_tfs:
            query_tfs[term] = 0
        query_tfs[term] = query_tfs[term] + 1


    doc_scores = calculate_document_scores(query_tfs, dictionary, postings_fo)
    
    def sort_key(doc_score):
        # Descending order of score, and uses smaller doc ID to break ties.
        return -doc_score[1], doc_score[0]

    search_results = heapq.nsmallest(K, doc_scores.items(), key=sort_key)
    return map(lambda x: x[0], search_results)


def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('running search on the queries...')

    # { word_type : (idf, offset_bytes) } 
    f = open(dict_file, 'rb')
    dictionary = pickle.load(f)
    f.close()

    postings_fo = open(postings_file, "rb")
    results_fo = open(results_file, "wt")

    line_num = 1
    line = linecache.getline(queries_file, line_num)
    while line != '':
        search_results = perform_search_query(line, dictionary, postings_fo)

        # Write results to output file
        search_results_str = ' '.join([str(docID) for docID in search_results]) + '\n'
        results_fo.write(search_results_str)

        line_num += 1
        line = linecache.getline(queries_file, line_num)
    
    postings_fo.close()
    results_fo.close()


dictionary_file = postings_file = file_of_queries = output_file_of_results = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file  = a
    elif o == '-p':
        postings_file = a
    elif o == '-q':
        file_of_queries = a
    elif o == '-o':
        file_of_output = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None :
    usage()
    sys.exit(2)

run_search(dictionary_file, postings_file, file_of_queries, file_of_output)
