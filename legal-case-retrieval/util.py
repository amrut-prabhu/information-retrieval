from collections import defaultdict
import nltk
import os
import math
from math import sqrt
import heapq
import string
import sys


REMOVE_PUNCTUATION = True
STEMMER = nltk.stem.porter.PorterStemmer()

def preprocess_content(content):
    """
    Preprocess the tokenzied/stemmed words in each document.

    :param content: raw tokens for each document
    :return: list of normalised tokens
    """
    terms = []

    sentences = nltk.tokenize.sent_tokenize(content)

    for sentence in sentences:
        if REMOVE_PUNCTUATION:
            exclude = set(string.punctuation)
            sentence = ''.join(ch for ch in sentence if ch not in exclude)
            
        words = nltk.tokenize.word_tokenize(sentence)
        for word in words:
            terms.append(STEMMER.stem(word.lower()))

    return terms


def format_results(results):
    """
    Formats result as required for output file.

    :param results: List of doc IDs.  [10, 3, 7]
    
    :return: formatted string. '10 3 7'
    """
    return ' '.join([str(docID) for docID in results]) + '\n'


def log10(x):
    """
    Returns log base 10 for positive input, and zero otherwise.
    """
    if x > 0:
        return math.log(x, 10)
    
    return 0


def positional_intersect(has_2_terms, postings1, postings2, postings3='dummy'):
    """
    Performs positional intersect for the postings lists and returns matching documents.

    Params:
        has_2_terms: Whether the phrasal query has 2 terms. If so, 3rd positional index is unused.
        postings1, postings2: Positional index [ (docID, positions, log-tf), ... ]
        postings3: If phrasal query has 3 terms, then positional index [ (docID, positions, log-tf), ... ]

    Returns:
        postings: [ (docID, log-tf) ]
    """

    i, j, k = 0, 0, 0
    len1, len2, len3 = len(postings1), len(postings2), len(postings3)

    postings = []
    while i < len1 and j < len2 and k < len3:
        # If document IDs are the same
        if postings1[i][0] == postings2[j][0] and (has_2_terms or postings3[k][0] == postings2[j][0]):
            curr_document = postings1[i][0]

            positions1 = postings1[i][1]
            positions2 = postings2[j][1]
            positions3 = 'dummy' if has_2_terms else postings3[k][1]

            poslen1, poslen2, poslen3 = len(positions1), len(positions2), len(positions3)

            phrasal_term_freq = 0

            # Get term frequency for phrasal query in this document
            x = 0
            while x < poslen1:
                y = 0
                while y < poslen2:
                    if positions2[y] == positions1[x] + 1:
                        if has_2_terms:
                            phrasal_term_freq += 1
                            break

                        else:
                            did_find_doc = False

                            z = 0
                            while z < poslen3:
                                if positions3[z] == positions2[y] + 1:
                                    phrasal_term_freq += 1

                                    did_find_doc = True
                                    break
                                elif positions3[z] > positions2[y]:
                                    break
                                else:
                                    z += 1

                            if did_find_doc:
                                break
                            else:
                                y += 1

                    elif positions2[y] > positions1[x]:
                        break
                    else:
                        y += 1

                x += 1

            # Add document to postings if phrasal query occurs in it
            if phrasal_term_freq > 0:
                postings.append((curr_document, 1 + log10(phrasal_term_freq)))

            i += 1
            j += 1
            k += 0 if has_2_terms else 1

        elif has_2_terms:  # Update pointers of 2 query postings
            if postings1[i][0] < postings2[j][0]:
                i += 1
            else:
                j += 1

        else:  # Update pointers of 3 query postings
            if postings1[i][0] <= postings2[j][0]:
                if postings1[i][0] <= postings3[k][0]:
                    i += 1
                else:
                    k += 1
            else:
                if postings2[j][0] <= postings3[k][0]:
                    j += 1
                else:
                    k += 1

    return postings


def has_skip(idx, skip_len, total_len):
    """
    Returns True if a non-zero logical skip pointer can be used to 
    skip a few steps forward.
    """
    if skip_len == 0:
        return False

    # sqrt(total_len) skip pointers are evenly placed 
    if idx % skip_len == 0 and (idx + skip_len) < total_len:
        return True

    return False


def perform_and_operation(list_1, list_2):
    """
    Performs intersection of the 2 postings lists.
    Sets term frequency in the result to the minimum from the documents in 
    the 2 input lists.

    Params:
        - list_1: Postings list [ (docID, log-tf), ... ]
        - list_2: Postings list [ (docID, log-tf), ... ]

    Returns:
        - results: Intersected postings list [ (docID, log-tf), ... ]
    """
    # DUMMY_LOG_TF = 1

    skip_1 = int(math.sqrt(len(list_1)))
    skip_2 = int(math.sqrt(len(list_2)))

    i = 0
    j = 0

    len1 = len(list_1)
    len2 = len(list_2)

    results = []
    while i < len1 and j < len2:
        if list_1[i][0] == list_2[j][0]:
            results.append((list_1[i][0], min(list_1[i][1], list_2[j][1])))

            i += 1
            j += 1
        elif list_1[i][0] < list_2[j][0]:
            # Check if skip pointer can be used
            if has_skip(i, skip_1, len1) and list_1[i + skip_1][0] <= list_2[j][0]:
                i += skip_1

                while has_skip(i, skip_1, len1) and list_1[i + skip_1][0] <= list_2[j][0]:
                    i += skip_1
            else:
                i += 1

        elif list_2[j][0] < list_1[i][0]:
            # Check if skip pointer can be used
            if has_skip(j, skip_2, len2) and list_2[j + skip_2][0] <= list_1[i][0]:
                j += skip_2

                while has_skip(j, skip_2, len2) and list_2[j + skip_2][0] <= list_1[i][0]:
                    j += skip_2
            else:
                j += 1

    return results

