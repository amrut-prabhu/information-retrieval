# Ranked Retrieval Search Engine

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
python search.py -d dictionary.txt -p postings.txt -q sample_queries1.txt -o output.txt
```

## General Notes

### Indexing phase

There are 2 parts for the indexing phase - creating the postings lists for all words, and using it to create a dictionary these that can be stored in memory.

1. For each document, the term frequencies are computed after tokenization, stemming and case folding.
This information is then added to the postings lists of the corresponding words as `(doc ID, normalized log term frequency)`. 
These are the tf-idf weights of the term for the document under the lnc.ltc ranking scheme.

2. Next, the postings list of each word is written to a file.
While doing so, a dictionary of the form `{ word_type : (idf, offset_bytes) } ` is created.
It stores information about the inverse document frequency, and the position of the posting list of each word.
This dictionary is then written to a file.

### Searching phase

The search query is first tokenized, stemmed and case folded.
The tokens are then used to compute the term frequencies of the query.
These are then converted to weights by multiplying log tf with idf. 
The cosine normalization is not done for query weights as we only want a relative ordering of scores.
To calculate document scores, dot product between normalized document weights and query weights is done, retrieving postings list for terms from the disk.
The top 10 document IDs are then selected from the scores using `heapq` and a custom sort key.

## Files 

- `index.py`: Creates and saves a search index from the documents that will be searched.
- `search.py`: Uses the search index to find up to the top 10 most relevant results for the queries.
- `dictionary.txt`: Dictionary containing information about the idf and position of postings list in the file for all words in the dictionary.
- `postings.txt`: The postings lists that belong to the search index.

## References

- Google, StackOverflow, GeeksForGeeks, Python docs: for Python syntax and errors
- StackOverflow (https://stackoverflow.com/questions/53062137/key-function-for-heapq-nlargest): For getting most relevant documents in right order using heapq
- NLTK documentation (https://www.nltk.org/api/nltk.tokenize.html): usage of functions like tokenize, PorterStemmer
- linecache documentation (https://docs.python.org/3/library/linecache.html): usage of getline function
- Introduction to Information Retrieval textbook: for scoring algorithm
- NUS CS3245 Luminus forum: for sample queries and outputs, clarifications about the score computation
