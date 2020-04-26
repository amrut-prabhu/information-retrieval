# Boolean Retrieval Search Engine

## Usage

### Building the index from documents

The `directory-of-documents` used is the Reuters training data set from NLTK. 
To download this, execute `nltk.download()` in a Python interpreter and download the data to an appropriate location.
In the downloaded files, the `/corpora/reuters/training/` directory contains the documents that will be indexed.

This indexing phase writes to two output files- `dictionary-file` and `postings-file`.

```sh
python index.py -i directory-of-documents -d dictionary-file -p postings-file

# Example
python index.py -i /c/users/amrut/cs3245/nltk_data/corpora/reuters/training/ -d dictionary.txt -p postings.txt
```

> It takes ~1 minute to index the 7,769 Reuters documents.

### Performing search queries

Queries to be tested are stored in `file-of-queries` with one query per line.
The output corresponding to each query is written to `output-file-of-results`.

```sh
python search.py -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results

# Example
python search.py -d dictionary.txt -p postings.txt -q sample_queries.txt -o output.txt
```

## General Notes

### Indexing phase

There are 2 parts for the indexing phase - creating the postings lists for all words, and using it to create a dictionary these that can be stored in memory.

1. The documents are parsed in increasing order of document ID in order to maintain sorted postings lists. 
After performing tokenization (at the sentence and word level), the word tokens are stemmed using Porter Stemming and case-folded to lower case. 
The words and document ID are then inserted into a `postings_lists` dict of the form `{ word: [docID, ...] }` after checking that there will not be duplicate document IDs in the list.
A special word token is used to store the list of all document IDs (for NOT queries).

2. Next, the postings list of each word is written as plain text to a file.
At the same time, a `dictionary` of the form `{ word_type: (offset_bytes, size_bytes, skip_len) }` is created.
It stores information about the position of the posting list of each word in the file, and the lengths of the postings list and the skip pointer.
The `dictionary` is then written to a file.

### Searching phase

The query is first parsed into Postfix notation using the Shunting Yard algorithm. 
The search terms undergo the same processing performed during indexing (stemming and case-folding).
The postfix expression is then evaluated using the appropriate algorithm (NOT, AND, OR) to merge lists of document IDs.
During evaluation of a query, the postings list of the word token is retrieved from the disk using the position information stored in the `dictionary`.
For out of vocabulary words, an empty postings list is returned. 

Some optimisations include processing AND NOT, NOT NOT queries, and using skip pointers for the postings lists and intermediate results of sub-queries as well.

The skip pointers are implemented as "logical" skip pointers instead of storing positions of the next element in the file. 
This reduces the space taken up by postings.txt on the disk.
This may come at the cost of more time taken during searching, but this may be offset by the less time taken to read less bytes from disk.

## Files 

- `index.py`: Creates and saves a search index from the documents that will be searched.
- `search.py`: Uses the search index to find results matching boolean queries.
- `dictionary.txt`: Dictionary containing information about the postings list size, position in the file, number of bytes to be read, and the length of skip pointers for all words in the dictionary.
- `postings.txt`: The postings lists that belong to the search index.

## References

- Google, StackOverflow, GeeksForGeeks, Python docs: for Python syntax and errors
- NLTK documentation (https://www.nltk.org/api/nltk.tokenize.html): usage of functions like tokenize, PorterStemmer
- linecache documentation (https://docs.python.org/3/library/linecache.html): usage of getline function
- Shunting Yard algorithm (https://en.wikipedia.org/wiki/Shunting-yard_algorithm): to parse the boolean queries
- Evaluating Reverse Polish Notation (https://en.wikipedia.org/wiki/Reverse_Polish_notation#Postfix_evaluation_algorithm): to evaluate the search query in Reverse Polish Notation form
- Introduction to Information Retrieval textbook: for size of the skip pointers and how to use it in the merging algorithm for postings lists
- NUS CS3245 Luminus forum: for sample queries and expected outputs
