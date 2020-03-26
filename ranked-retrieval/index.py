#!/usr/bin/python3
import re
import nltk
import sys
import getopt

import math
import os
import linecache
import _pickle as pickle

from dictionary import Dictionary
from postings_lists import PostingsLists

def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")


def get_sorted_file_names(in_dir):
    """
    Returns the list of file names of the documents to be indexed, sorted by their document IDs.
    In this case, the file name acts as the document ID.

    Input:
        in_dir:

    Output:
        files:
    """
    # Convert file names to int to sort in natural numerical order
    files = [int(f) for f in os.listdir(in_dir) if os.path.isfile(os.path.join(in_dir, f))]
    files.sort() 

    return files        


def create_postings_lists(in_dir):
    """
    Returns the postings lists created from the documents in `in_dir`.
    Applies sentence and word level tokenisation, stemming and case folding.

    Input:
        in_dir:

    Output:
        postings_lists:
        document_lengths: 
        collection_size:
    """
    # { word_type : [ (doc_id, term_freq), ... ] }
    postings_lists = {} 

    # { doc_id: num_words }
    document_lengths = {}

    stemmer = nltk.stem.porter.PorterStemmer()
    files = get_sorted_file_names(in_dir) # Get sorted names, since postings list should have sorted doc IDs

    for docID in files:
        file_path = os.path.join(in_dir, str(docID))

        doc_length = 0

        line_num = 1
        line = linecache.getline(file_path, line_num)

        while line != '':
            for sent_token in nltk.sent_tokenize(line):
                for word_token in nltk.word_tokenize(sent_token):
                    # Apply stemming and case folding after tokenization
                    stemmed_word_token = stemmer.stem(word_token).lower()

                    doc_length += 1

                    # Add doc ID to postings list
                    if stemmed_word_token not in postings_lists:
                        postings_lists[stemmed_word_token] = []

                    postings = postings_lists[stemmed_word_token]

                    if (len(postings) == 0 or postings[-1][0] != docID):
                        postings.append((docID, 1))
                    else: # postings[-1][0] == docID
                        postings[-1] = (docID, postings[-1][1] + 1)

            line_num += 1
            line = linecache.getline(file_path, line_num)

        document_lengths[docID] = compute_doc_length(docID)

    collection_size = len(files) # Total number of documents in the collection

    return postings_lists, document_lengths, collection_size


def log10(x):
    if x == 0:
        return 0
    
    return math.log(x, 10)

def write_postings_list(postings_list, f):
    """
    Returns the size of the stringified postings list written to the file.

    eg. [1, 2, 5, 21] gets stringified to "1,2,5,21 " and returns 9.

    Input:
        postings_list:
        f:

    Output:

    """
    # TODO: use pickle dump
    postings_list_str = ','.join([str(docID) for docID in postings_list]) + ' '

    f.write(postings_list_str)

    return len(postings_list_str)


def process_and_write_index_to_disk(postings_lists, document_lengths, out_dict, out_postings):
    """
    Writes the postings lists and the in-memory dictionary to the output files.

    Input:
        postings_lists: 
        document_lengths: 
        out_dict:
        out_postings:

    Output:
        None
    """
    # { 
    #   word_type : (
    #       doc_freq,     # Number of documents containing this word, i.e., document frequency
    #       offset_bytes, # Position offset from start of postings file
    #       size_bytes   # Size of postings list written for this word
    #   ) 
    # } 
    dictionary = {} 

    # Write postings lists to output file, and create the dictionary
    f = open(out_postings, 'w')

    offset = 0 # Number of bytes that have been written to file
    for word in postings_lists:
        doc_freq = len(postings_lists[word])
        idf = log()

        size_bytes = write_postings_list(postings_lists[word], f)

        dictionary[word] = (doc_freq, offset, size_bytes)
        offset += size_bytes

    f.close()

    # Write dictionary and documentlengths to output file
    d = { 
        'document_lengths': document_lengths, # TODO:
        'dictionary': dictionary
    }
    
    f = open(out_dict, 'wb')
    pickle.dump(d, f)
    f.close()


def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print('indexing...')

    postings_lists, document_lengths, collection_size = create_postings_lists(in_dir)

    process_and_write_index_to_disk(postings_lists, document_lengths, out_dict, out_postings)


input_directory = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-i': # input directory
        input_directory = a
    elif o == '-d': # dictionary file
        output_file_dictionary = a
    elif o == '-p': # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"

if input_directory == None or output_file_postings == None or output_file_dictionary == None:
    usage()
    sys.exit(2)

build_index(input_directory, output_file_dictionary, output_file_postings)
