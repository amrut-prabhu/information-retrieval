from collections import Counter, defaultdict
import util
from math import sqrt

ALPHA = 0.8
BETA = 0.3
GAMMA = 0.1  # Because getting non-relevant docs vector is time consuming


def get_document_vector(docId, dictionary, postings_file):

    doc_vector = dict()
    for term in dictionary.get_terms():
        offset, size = dictionary.get_offset_and_size_of_term(term)
        term_postings = dict(postings_file.get_posting_list(offset, size))

        if docId in term_postings:
            doc_vector[term] = int(round(10**(term_postings[docId] - 1)))

    return doc_vector
    # print(doc_vector)

def get_docs_vectors(docs, dictionary, postings_file):
    docs_vector_dict = defaultdict(lambda: defaultdict(float))

    for term in dictionary.get_terms():
        offset, size = dictionary.get_offset_and_size_of_term(term)
        term_postings = dict(postings_file.get_posting_list(offset, size))

        for doc in docs:
            if doc in term_postings:
                docs_vector_dict[doc][term] = term_postings[doc]

    return docs_vector_dict

def rocchio(query, relevant_docs, dictionary, postings_file, non_relevant_docs=None):
    relevant_docs_vector = get_docs_vectors(relevant_docs, dictionary, postings_file)
    if non_relevant_docs is not None:
        non_relevant_docs_vector = get_docs_vectors(non_relevant_docs, dictionary, postings_file)
    else:
        non_relevant_docs_vector = {}

    query_ctr = dict(query)
    num_of_relevant_docs = len(relevant_docs)
    num_of_non_relevant_docs = 0 if non_relevant_docs is None else len(non_relevant_docs)

    relevant_docs_terms = []
    for docId, docVector in relevant_docs_vector.items():
        relevant_docs_terms = relevant_docs_terms + list(docVector.keys())

    relevant_terms_idf = []
    for relevant_term in relevant_docs_terms:
        relevant_terms_idf.append((dictionary.get_df(relevant_term), relevant_term))

    sorted_relevant_terms = sorted(relevant_terms_idf, key=lambda x: x[0], reverse=True)
    top_relevant_terms = [x[1] for x in sorted_relevant_terms[:10]]

    non_relevant_docs_terms = []
    for docId, docVector in non_relevant_docs_vector.items():
        non_relevant_docs_terms = non_relevant_docs_terms + list(docVector.keys())

    all_terms = list(set(non_relevant_docs_terms + top_relevant_terms + list(query_ctr.keys())))

    new_query = defaultdict(float)
    for term in all_terms:
        if term in query_ctr:
            new_query[term] += ALPHA * query_ctr[term]

        sum_relevant = 0
        normalised_relevant = 0
        for docId, doc_vector in relevant_docs_vector.items():
            if term in doc_vector:
                sum_relevant += doc_vector[term]
                normalised_relevant += (doc_vector[term] * doc_vector[term])

        if sum_relevant > 0:
            new_query[term] += BETA * (sum_relevant / sqrt(normalised_relevant))

        sum_non_relevant = 0
        normalised_non_relevant = 0
        for docId, doc_vector in non_relevant_docs_vector.items():
            if term in doc_vector:
                sum_non_relevant += doc_vector[term]
                normalised_non_relevant += (doc_vector[term] * doc_vector[term])

        if sum_non_relevant > 0:
            new_query[term] -= GAMMA * (sum_non_relevant / sqrt(normalised_non_relevant))

    return new_query



