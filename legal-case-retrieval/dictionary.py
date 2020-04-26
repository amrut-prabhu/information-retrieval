import pickle

from math import sqrt, log
from posting import Posting
import util

class Dictionary(object):
    """
    Getter and Setter functions related to the dictionary index.
    Store on disk and accessed using pickle.
    Tracks normalised docs lengths, and total number of docs.
    """
    def __init__(self, disk_file):
        self.terms = {}  # { term: { offset: int, docFreq: int, posting: Posting}}
        self.court_weights = {}  # { docID: court_weight }
        self.disk_file = disk_file  # File name where dictionary is stored in disk
        self.num_of_docs = 0  # Total number of documents in collection
        self.normalised_doc_lengths = {}  #  { doc_id: normalized_length } where normalized_length = sqrt(sum((1+log(tf)^2)))


    def add_tokens_of_doc(self, content, docId):
        """
        Processes content of this document and updates indices and postings lists.

        Params:
            - content: tokens in the document content
            - docId: document ID
        
        Returns:
            - normalised_tf: normalised length of document
        """
        tf_freq = {} # Term frequencies of this document

        position = 0 # position of token in content
        for token in content:
            if token not in self.terms:
                self.terms[token] = {}
                self.terms[token]["offset"] = None
                self.terms[token]["size"] = None
                self.terms[token]["docFreq"] = 1
                self.terms[token]["posting"] = Posting()
            else:
                if token not in tf_freq:
                    self.terms[token]["docFreq"] += 1

            self.terms[token]["posting"].add_doc_to_postings(docId)
            self.terms[token]["posting"].add_pos_to_doc(docId, position)

            position += 1

            if token in tf_freq:
                tf_freq[token] += 1
            else:
                tf_freq[token] = 1


        normalised_tf = 0
        for token in tf_freq.keys():
            freq = tf_freq[token]
            normalised_tf += pow((1 + util.log10(freq)), 2)

        return sqrt(normalised_tf)


    def format_dict_for_saving_postings(self, term):
        posting_list = self.terms[term]["posting"]
        return posting_list


    def update_offset_and_size(self, term, offset, size):
        del self.terms[term]["posting"]
        self.terms[term]["offset"] = offset
        self.terms[term]["size"] = size


    def get_terms(self):
        """
        Gets all terms dictionary
        :return: terms with frequency and offset
        """
        return self.terms


    def get_df(self, token):
        """
        Gets the Document frequency for a term.
        Returns -1 if term not present
        :param token: term
        :return: int representing documentFrequency for the term
        """
        if token in self.terms:
            return self.terms[token]["docFreq"]
        else:
            return -1


    def get_offset_and_size_of_term(self, term):
        """
        Gets offset to seek to for posting list in posting file, and 
        number of bytes to read
        :param term: normalised term
        :return: -1 if term not present and offset if term present
        """
        if term in self.terms:
            return self.terms[term]["offset"], self.terms[term]["size"]
        else:
            return -1, -1


    def add_normalised_doc_length(self, doc_id, normalized_length):
        """
        Sets the normalised length of the document.
        normalized_length = sqrt( sum(1 + log(tf)^2) )

        :param doc_id: docId for which it is to be set
        :param normalized_length: normalised sum of term frequencies for a doc
        """
        self.normalised_doc_lengths[doc_id] = normalized_length


    def get_normalised_doc_length(self, doc_id):
        """
        Returns the normalised length of the document.

        :param doc_id: document ID
        :return: float normalised length of document.
        """
        return self.normalised_doc_lengths[doc_id]


    def add_court_weight(self, doc_id, court_weight):
        """
        Sets the weight of the term frequencies for the document, based on importance of court.

        :param doc_id: docId for which it is to be set
        :param court_weight: weight for term frequencies of doc
        """
        self.court_weights[doc_id] = court_weight


    def get_court_weight(self, doc_id):
        """
        Returns the weight of the term frequencies of the document.

        :param doc_id: document ID
        :return: term frequency weights
        """
        if doc_id not in self.court_weights:
        	return 1

        return self.court_weights[doc_id]


    def add_doc_count(self):
        """
        Increment doc count of collection.
        """
        self.num_of_docs += 1


    def get_doc_count(self):
        """
        Gets the total number of docs in collection.
        :return: integer
        """
        return self.num_of_docs


    def save(self):
        """
        Saves dictionary dict() using pickle dump
        in dict format as {terms: {}, normalised_doc_lengths: {}, num_of_docs: int}
        """
        with open(self.disk_file, 'wb') as f:
            pickle.dump({
                "terms": self.terms,
                "court_weights": self.court_weights,
                "normalised_doc_lengths": self.normalised_doc_lengths,
                "num_of_docs": self.num_of_docs}, f)
        f.close()


    def load(self):
        """
        Loads dictionary from disk and stores in the Dictionary in memory object
        in dict format as {terms: {}, normalised_doc_lengths: {}, num_of_docs: int}
        """
        with open(self.disk_file, 'rb') as f:
            res = pickle.load(f)
            self.terms = res["terms"]
            self.court_weights = res["court_weights"]
            self.normalised_doc_lengths = res["normalised_doc_lengths"]
            self.num_of_docs = res["num_of_docs"]

        f.close()
