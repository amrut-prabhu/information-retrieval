class Posting(object):
    def __init__(self):
        self.docs = {}  # { docId: { "positions": [] } }  Term freq is computed from length of positions


    def add_doc_to_postings(self, docId):
        if docId not in self.docs:
            self.docs[docId] = {}
            self.docs[docId]["positions"] = []


    def add_pos_to_doc(self, docId, pos):
        self.docs[docId]["positions"].append(pos)


    def save_postings(self, posting_file):
        """
        Saves postings as "docID1#tf1#pos1,pos2,pos3 docID2#tf2#pos1,pos2 "
        
        Example: postings = { 
            222: { 'positions': [4,5,6,7,8] }, 
            111: { 'positions': [1,2,3] }, 
        }
        Output: 111#1,2,3 222#4,5,6,7,8
        """
        postings = self.docs

        docIDs = sorted(postings.keys())

        postings_list_str = ' '.join([
                str(docID) + "#" + 
                ','.join([str(pos) for pos in postings[docID]["positions"]]) 
                    for docID in docIDs]) + ' '

        posting_file.write(postings_list_str)

