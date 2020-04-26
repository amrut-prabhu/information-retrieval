import pickle
from collections import defaultdict

import util

class PostingsFile(object):
    """
    Getter and Setter functions related to the postings and posting list
    Also used to store on disk and access it using pickle and until functions
    """
    def __init__(self, file_name):
        self.disk_file = file_name

    def save(self, dictionary):
        with open(self.disk_file, 'wt') as postings_file:
            for token in dictionary.get_terms():
                offset = postings_file.tell()
                postings_list = dictionary.format_dict_for_saving_postings(token)

                postings_list.save_postings(postings_file)
                
                size = (postings_file.tell() - offset) - 1 # Don't read whitespace at end
                dictionary.update_offset_and_size(token, offset, size)

        postings_file.close()

    def parse_postings_with_positions(self, postings_str, dictionary):
        """
        Returns posintgs list of the form [ (docID, positions, log-tf), ... ] by
        reading and parsing from the disk. Document term frequencies are weighted
        by the importance of the corresponding court.

        Example:
            Input: 111#1,2,3 222#4,5,6,7,8
            Output: [
                ( 111, [1,2,3], 1.4771 ), 
                ( 222, [4,5,6,7,8], 1.6989 ), 
            ]
        """
        postings = postings_str.split(' ')

        postings_list = []
        for posting in postings:
            [docID, positions] = posting.split('#')
            positions = [int(pos) for pos in positions.split(',')]
            
            tf_weight = dictionary.get_court_weight(docID)

            tf = len(positions) * tf_weight
            log_tf = 1 + util.log10(tf)

            postings_list.append((int(docID), positions, log_tf))

        return postings_list
    

    def get_posting_list_with_positions(self, offset, size, dictionary):
        """
        Gets posting list for a given offset in file
        :param offset: the offset to seek to in file
        """
        with open(self.disk_file, 'rt') as postings_file:
            postings_file.seek(offset)
            postings_str = postings_file.read(size)

            postings_list = self.parse_postings_with_positions(postings_str, dictionary)

            return postings_list



    def parse_postings(self, postings_str, dictionary):
        """
        Returns [ (docID, log-tf), ... ]

        Example:
            Input: 111#1,2,3 222#4,5,6,7,8
            Output: [
                ( 111, 1.4771 ), 
                ( 222, 1.6989 ), 
            ]
        """
        postings = postings_str.split(' ')

        postings_list = []
        for posting in postings:
            [docID, positions] = posting.split('#')

            tf_weight = dictionary.get_court_weight(docID)

            tf = len(positions) * tf_weight
            log_tf = 1 + util.log10(tf)

            postings_list.append((int(docID), log_tf))

        return postings_list


    def get_posting_list(self, offset, size, dictionary):
        """
        Gets posting list for a given offset in file
        :param offset: the offset to seek to in file
        """
        with open(self.disk_file, 'rt') as postings_file:
            postings_file.seek(offset)
            postings_str = postings_file.read(size)

            postings_list = self.parse_postings(postings_str, dictionary)

            return postings_list

