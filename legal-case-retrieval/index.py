#!/usr/bin/python3
import re
from collections import defaultdict

import nltk
import sys
import getopt
import os
import csv

import util
from dictionary import Dictionary
from postingsfile import PostingsFile
import court 


maxInt = sys.maxsize
while True:
    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt/10)


def usage():
    print("usage: " + sys.argv[0] + " -i dataset-file -d dictionary-file -p postings-file")


def process_csv(dataset_file, out_dict):
    """
    Parses and processes the CSV data file to create the index and postings lists.

    Params:
        - dataset_file: Path to dataset
        - out_dict: Path to save dictionary to

    Returns:
        - dictionary: Dictionary containing index and postings
    """
    dictionary = Dictionary(out_dict)

    with open(dataset_file, encoding="utf8") as dataset_csv:
        i = 0
        prev_docId = 0

        csv_reader = csv.reader(dataset_csv)
        for row in csv_reader:
            i += 1

            # Skip CSV header
            if i == 1:
                continue

            docId = row[0]

            # Skip duplicate document IDs
            if prev_docId == docId:
                continue
            
            # For each document, get the content tokens and add it to the posting lists
            tokens = util.preprocess_content(row[1] + " " + row[2] + " " + row[3] + " " + row[4])
            normalised_tf = dictionary.add_tokens_of_doc(tokens, docId)

            # Maintain document lengths and count in dictionary
            dictionary.add_normalised_doc_length(docId, normalised_tf)
            dictionary.add_court_weight(docId, court.get_court_weight(row[4]))
            dictionary.add_doc_count()

            prev_docId = docId

    dataset_csv.close()

    return dictionary


def build_index(dataset_file, out_dict, out_postings):
    """
    build index from documents stored in the dataset file,
    then output the dictionary file and postings file
    """
    print('indexing...')

    postings_file = PostingsFile(out_postings)

    dictionary = process_csv(dataset_file, out_dict)

    # Save dictionary and postings lists to disk
    postings_file.save(dictionary)
    dictionary.save()


dataset_file = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-i': # dataset file
        dataset_file = a
    elif o == '-d': # dictionary file
        output_file_dictionary = a
    elif o == '-p': # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"

if dataset_file == None or output_file_postings == None or output_file_dictionary == None:
    usage()
    sys.exit(2)

build_index(dataset_file, output_file_dictionary, output_file_postings)
