#!/usr/bin/python3
import re
import nltk
import sys
import getopt

import math
import os
import linecache
import _pickle as pickle

def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")


def get_sorted_file_names(in_dir):
    """
    Returns the list of file names of the documents to be indexed, sorted by their document IDs.
    In this case, the file name acts as the document ID.
    """
    # Convert file names to int to sort in natural numerical order
    files = [int(f) for f in os.listdir(in_dir) if os.path.isfile(os.path.join(in_dir, f))]
    files.sort() 

    return files        


def log10(x):
    """
    Returns log base 10 for positive input, and zero otherwise.
    """
    if x > 0:
        return math.log(x, 10)
    
    return 0


def get_document_vector_length(doc_tfs):
    """
    Returns the L2 norm of the document vector using weighted term frequencies.

    Input:
        doc_tfs: Raw term frequency counts for this document { word_type: tf }
    """
    return math.sqrt(sum(map(lambda kv: pow(1 + log10(kv[1]), 2), doc_tfs.items())))


def add_doc_tf_to_postings(doc_id, doc_tfs, postings_lists):
    """
    Updates the postings lists by adding the doc ID and normalized term 
    frequency weights to the postings of word types.

    Input:
        doc_id: Document ID
        doc_tfs: Raw term frequencies for the word types in this document
        postings_lists: Postings lists with all word types
    """
    doc_length = get_document_vector_length(doc_tfs)

    for word_type, raw_tf in doc_tfs.items(): 
        n_wt = (1 + log10(raw_tf)) / doc_length

        if word_type not in postings_lists:
            postings_lists[word_type] = []
        postings_lists[word_type].append((doc_id, n_wt))


def create_postings_lists(in_dir):
    """
    Returns the postings lists created from the documents in `in_dir`.
    Applies sentence and word level tokenisation, stemming and case folding.

    Input:
        in_dir: Directory containing the documents in the collection.

    Output:
        postings_lists: Postings lists for all word types
        collection_size: Number of documents in the collection
    """
    # { word_type : [ (doc_id, n_wt), ... ] } # Tuples of docIDs and normalized term frequency weights
    postings_lists = {} 

    stemmer = nltk.stem.porter.PorterStemmer()
    files = get_sorted_file_names(in_dir)

    for doc_id in files:
        file_path = os.path.join(in_dir, str(doc_id))

        doc_tfs = {}

        line_num = 1
        line = linecache.getline(file_path, line_num)
        while line != '':
            for sent_token in nltk.sent_tokenize(line):
                for word_token in nltk.word_tokenize(sent_token):
                    # Apply stemming and case folding after tokenization
                    stemmed_word_token = stemmer.stem(word_token).lower()

                    # Increment document's term frequency
                    if stemmed_word_token not in doc_tfs:
                        doc_tfs[stemmed_word_token] = 0
                    doc_tfs[stemmed_word_token] = doc_tfs[stemmed_word_token] + 1

            line_num += 1
            line = linecache.getline(file_path, line_num)


        # Add doc ID and weights to postings list
        add_doc_tf_to_postings(doc_id, doc_tfs, postings_lists)


    collection_size = len(files) # Total number of documents in the collection

    return postings_lists, collection_size
    

def write_index_to_disk(postings_lists, collection_size, out_dict, out_postings):
    """
    Writes the postings lists and the in-memory dictionary to the output files.

    Input:
        postings_lists: { word_type: [ (doc_id, n_wt), ... ] }
        collection_size: Total number of documents, N
        out_dict: Output file for dictionary
        out_postings: Output file for postings lists
    """
    # { word_type : (idf, offset_bytes) } 
    # Inverse document frequency, and Position offset from start of postings file
    dictionary = {} 

    # Write postings lists to output file, and create the dictionary
    f = open(out_postings, 'wb')

    offset = 0 # Number of bytes that have been written to file
    for word in postings_lists:
        pickle.dump(postings_lists[word], f)

        df = len(postings_lists[word])
        idf = log10(collection_size / df)
        dictionary[word] = (idf, offset)
        
        offset = f.tell() 

    f.close()

    # Write dictionary to output file
    f = open(out_dict, 'wb')
    pickle.dump(dictionary, f)
    f.close()


def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print('indexing...')

    postings_lists, collection_size = create_postings_lists(in_dir)

    write_index_to_disk(postings_lists, collection_size, out_dict, out_postings)


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
