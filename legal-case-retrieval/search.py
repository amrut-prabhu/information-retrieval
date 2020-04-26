#!/usr/bin/python3
import sys
import getopt
import util
import linecache
import math
from collections import defaultdict
from spellchecker import SpellChecker
import heapq

from nltk.corpus import wordnet
import rocchio
from nltk.wsd import lesk

from dictionary import Dictionary
from postingsfile import PostingsFile
from extended_boolean import extended_boolean_p_norm_model
import tf_idf
import query_expansion
import boolean


def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q query-file -o output-file-of-results")


def parse_query(query_str):
    """
    Possible Inputs: 
        - Free text: quite phone call
        - Boolean and phrasal queries: "fertility treatment" AND damages AND "medicine" and sick

    Returns:
        - is_boolean_query: whether it is a boolean query
        - query: list of query tokens [term, ...]
    """
    is_boolean_query = "AND" in query_str

    if is_boolean_query:
        query = [query_term.strip() for query_term in query_str.split('AND')]
    else:
        # Free text query
        query = util.preprocess_content(query_str)

    return is_boolean_query, query


def run_search(dict_file, postings_file, query_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given query file and output the results to a file
    """
    postings = PostingsFile(postings_file)

    # Load index into memory
    dictionary = Dictionary(dict_file)
    dictionary.load()

    output_f = open(results_file, 'wt')

    line_num = 1
    query_str = linecache.getline(query_file, line_num)

    is_boolean_query, query = parse_query(query_str)

    new_query = query_expansion.query_expansion_thesaurus(query_str)

    if is_boolean_query:
        results_bool = boolean.eval_boolean_query(query, dictionary, postings)
        results_ex_bool = boolean.eval_extended_boolean_query(query, dictionary, postings)
        results_lnc = tf_idf.eval_free_text_query(new_query, dictionary, postings, True)

        results = boolean.rank_results_bool(results_bool, results_ex_bool, results_lnc)
    else:
        results = tf_idf.eval_free_text_query(new_query, dictionary, postings)

        # Rocchio
        # query_rocchio = rocchio.rocchio(query_str, results[:3], dictionary, postings)
        # results = tf_idf.eval_free_text_query(query_rocchio, dictionary, postings, is_boolean=False, is_rocchio=True)

    # Write results to file
    write_data = util.format_results(results)
    output_f.write(write_data)

    output_f.close()


dictionary_file = postings_file = query_file = file_of_output = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file = a
    elif o == '-p':
        postings_file = a
    elif o == '-q':
        query_file = a
    elif o == '-o':
        file_of_output = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or query_file == None or file_of_output == None:
    usage()
    sys.exit(2)

run_search(dictionary_file, postings_file, query_file, file_of_output)
