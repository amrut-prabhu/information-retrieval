#!/usr/bin/python3
import re
import nltk
import sys
import getopt

import linecache
import _pickle as pickle
import math

from dictionary import Dictionary
from postings_lists import PostingsLists

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")


def process_query(query):
    """
    Query terms processed using stemming and case folding.
    """
    output = []

    stemmer = nltk.stem.porter.PorterStemmer()
    tokens = nltk.word_tokenize(query)
    for token in tokens:
        # Apply stemming and case folding as done during indexing
        output.append(stemmer.stem(token).lower())

    return output


def read_postings_list_from_disk(word, dictionary, postings_fo):
    """
    Returns the postings list of the `word`, read from the postings file.
    """
    # TODO: time - use pickle to load serialized data instead. 
    # Store skip pointers on disk
    # Use f.tell() to store offsets in index.py
    (num_docs, offset, size, skip_len) = dictionary[word]
    
    postings_fo.seek(offset, 0)
    postings = postings_fo.read(size)
    postings = [int(docID) for docID in postings[:-1].split(',')] # Remove trailing space and convert to list

    return postings


# Wrapper tuple class to store list of document IDs and the length of the skip pointers for this list
QueryResult = namedtuple('QueryResult', ['doc_Ids', 'skip_len'])


def get_query_result(operand, dictionary, postings_fo):
    """
    Returns `operand` if it is a `QueryResult`. 
    Otherwise, read from the disk and return a QueryResult containing the postings list 
    of document IDs and length of skip pointers.
    """
    if type(operand) is QueryResult:
        return operand

    if operand not in dictionary:
        return QueryResult([], 0)

    postings_list = read_postings_list_from_disk(operand, dictionary, postings_fo)

    return QueryResult(postings_list, dictionary[operand][-1])



def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('running search on the queries...')

    # { word_type : (num_docs, offset_bytes, size_bytes, skip_len) } 
    f = open(dict_file, 'rb')
    dictionary = pickle.load(f)
    f.close()

    postings_fo = open(postings_file, "rt")
    results_fo = open(results_file, "wt")

    line_num = 1
    line = linecache.getline(queries_file, line_num)
    while line != '':
        # TODO: lnc.ltc ranking scheme 
        # i.e. For QUERIES documents, log tf and idf with cosine normalization
        # For DOCUMENTS, log tf, cosine normalization but no idf 
        
        # Cosine similarity with weights tf-idf = (1 + math.log(tf, 10)) * math.log(N/df, 10) # TODO: Take care of math.log(0, 10)


        query = shunting_yard(line) # process_query(line)
        search_results = perform_search_query(query, dictionary, postings_fo)
        
        # TODO: output a list of UP TO 10 most relevant document IDs
        # sorted by decreasing relevance and then doc ID (if same relevance)

        # Use Max Heap- You could set the max-heap to contain only 100 documents (fewer, if you'd like) 
        # and at the end of processing, just report the max 10

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
