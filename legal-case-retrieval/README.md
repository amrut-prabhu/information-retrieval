# Legal Case Retrieval - Structured Documents Search Engine

## Usage

### Building the index from documents

The `dataset-file` used is the legal corpus document collectionc(Intelllex) to retrieve from. 

This indexing phase writes to two output files- `dictionary-file` and `postings-file`.

```sh
python index.py -i dataset-file -d dictionary-file -p postings-file

# Example
python index.py -d dictionary.txt -p postings.txt -i '/c/Users/amrut/Documents/dataset.csv'
```

> It takes ~1.5 hours to index the 700 MB collection.

### Performing search queries

Queries to be tested are stored in individual files `query-file`.
All the relevant documents for each query are written to `output-file-of-results`, in sorted order of relevance.

```sh
python search.py -d dictionary-file -p postings-file -q query-file -o output-file-of-results

# Example
python search.py -d dictionary.txt -p postings.txt -q queries/q1.txt -o queries/q1.o
python search.py -d dictionary.txt -p postings.txt -q queries/q2.txt -o queries/q2.o
python search.py -d dictionary.txt -p postings.txt -q queries/q3.txt -o queries/q3.o
```

## General Notes

### Indexing:

In order to ensure fast and memory efficient indexing, we had to iterate over our indexing algorithm a couple of times to satisfy all constraints.

Our indexing process currently takes around 80-90 minutes. In the starting we took about 6-7 hours and then by using profiling and optimising our code we could bring it down to less than 2 hours.

1. We start by processing the CSV rows using a reader
2. For each row parsed we pre-process the content using sentence and word tokenisers and then stem using Porter algorithm
3. All the data is then store in an efficient and readable manner into the dictionary and posting class.
4. After all csv data is processed, we start by writing into postings file after taking each token one by one.
5. Once this is done we store offset and size in dictionary and start writing into dictionary file.

Initially, the posting file was around 1 GB because we stored it as python data structure. We then refactored to use plain text instead of using pickle, which can then be encoded and decoded to python data structures and hence got it to about 700 MB. 
The dictionary file is only 18 MB and hence can be completely loaded into memory.

Format of `dictionary.txt`: 
```py
{ 
    'terms': {
        { term: { 'offset': int, 'size': int, 'docFreq': int } }
    }, 
    'court_weights': { docId: float }, 
    'num_of_docs': int, 
    'normalised_doc_lengths': { docId: float }
}
```

Format of positional index postings list of a term in `postings.txt`: 
```
docID1#tf1#pos1,pos2,pos3 docID2#tf2#pos1,pos2
```

### Searching:

The search query is first parsed and processed into normalised tokens.

**Query expansion** is then performed on the query. 
This adds new query terms using synonymns, a "co-occurrence thesaurus" that uses context to add suitable synonyms, and spelling correction. 
In order to not shadow the original query, these additional terms are assigned different (and lower) query term weights, and only a fraction of  all possible additional query terms are added, based on relevance.

Depending on whether it is a free text query or a boolean query, the search procedure is:
- **Free text query**: The new expanded query is used to search for documents using the Vector Space model. 
The document term frequencies are also weighted according to the importances of courts, which was added during indexing. 
The tf-idf weights are calculated and used for scoring the documents. 
These results are then ranked and outputted. 

- **Boolean query**: For boolean queries (which may include phrasal queries containing 2-3 terms), a combination of results from the _Standard Boolean Model_, an _Extended Boolean Model_ (P-norm) which uses query-document similarity, and a _free text search_ on the expanded query is used. 

    Each of these methods assign scores to the results.
For the standard boolean model, the scores assigned to documents are the log term frequencies. 
For phrasal query terms, the minimum of the term frequencies of the terms is used since we only have AND queries. 
For the P-norm model, the query-document similarities (from 0 to 1) are computed, with scores close to 1 being better for AND queries.
For the free text retrieval model, the tf-idf model from above is used to assign scores.

    The scores of the methods are normalised to make them comparable across methods. 
A weighted sum of the scores is performed (choosing weights via heuristics and experimentation), and the final ranking is done using these scores.

    The standard boolean retrieves too few documents. 
The addition of free text query results improved the precision of our results. 
The extended boolean model softens the boolean constraint (using the P value, which we set to 1 after experimentation) and scores documents.

**Techniques implemented / experimented with**: Query refinements techniques like finding synonyms, then finding synonyms based on query context using LESK, Pseudo Relevance Feedback (PRF) using Rocchio's algorithm are implemented.

More details and experimental results can be found regarding query refinement in `Techniques.docx`.

## Final Results

The resultant Mean Average F2 scores for 6 queries (queries 1, 2, 4 and 6 are boolean phrasal; queries 3 and 5 are free text) is shown for the baseline TF×IDF ranked retrieval implementation, and the implementation in this repo.

| Implementation | Q1 Avg F2 | Q2 Avg F2 | Q3 Avg F2 | Q4 Avg F2 | Q5 Avg F2 | Q6 Avg F2 | Mean Avg F2 | 
| -------- | -------- | -------- | -------- | -------- | -------- | -------- | -------- |
| Baseline | 0.0108595077894779 | 0.362745098039216 | 0.0113111117361595 | 0.496296296296296 | 0.104510939130271 | 0.3 | 0.214287158831903 | 
| This repository's code | 0.016348874814715 | 0.283713200379867 | 0.00255552369327505 | 0.567390698969646 | 0.298479298479298 | 0.0792249821376035 | 0.20795209641 |


The tables below show the Average F score, Average Precision, Average Recall, Count of retrieved documents, and Number of correct retrieved documents.

**Baseline**:

| Query | Avg F | Avg P | Avg R | Count | Correct | 
| ------- | ------- | -------- | -------- | -------- | -------- | 
| result.1.txt | 0.0108595077894779 | 0.00226434047052604 | 0.5 | 16988 | 2 | 
| result.2.txt | 0.362745098039216 | 0.175641025641026 | 0.666666666666667 | 16988 | 3 | 
| result.3.txt | 0.0113111117361595 | 0.00233972270851163 | 0.625 | 16952 | 4 |
| result.4.txt | 0.496296296296296 | 0.299145299145299 | 0.666666666666667 | 16988 | 3 | 
| result.5.txt | 0.104510939130271 | 0.0239600720013091 | 0.666666666666667 | 6464 | 3 |
| result.6.txt | 0.3 | 0.260869565217391 | 0.75 | 16988 | 2 |

**This repository's code**:

| Query | Avg F | Avg P | Avg R | Count | Correct | 
| ------- | ------- | -------- | -------- | -------- | -------- | 
| result.1.txt | 0.016348874814715 | 0.00351105578037716 | 0.5 | 16992 | 2 | 
| result.2.txt | 0.283713200379867 | 0.0932539682539683 | 0.666666666666667 | 17137 | 3 | 
| result.3.txt | 0.00255552369327505 | 0.000515425312294806 | 0.625 | 17137 | 4 | 
| result.4.txt | 0.567390698969646 | 0.420634920634921 | 0.666666666666667 | 17004 | 3 | 
| result.5.txt | 0.298479298479298 | 0.107911898609573 | 0.666666666666667 | 17137 | 3 | 
| result.6.txt | 0.0792249821376035 | 0.020697350069735 | 0.75 | 16989 | 2 |  

## Files 

- Indexing:
    - `index.py`: To index the collection and save the index dictionary and postings on disk.
    - `dictionary.py`: To get the positions of postings list of terms, document frequency, lengths of documents, num of documents in the collection, and weights of courts of documents.
    - `posting.py`: To store the positional index postings and save them to disk.
    - `postingsfile.py`: To handle I/O operations related to posting file like saving  and retrieving postings from disk.
    - `court.py`: TO get the importance weights of courts for documents.
- Searching:
    - `search.py`: To parse the search query and store the relevant results in output file.
    - `query_expansion.py`: To perform query expansion using synonyms and spelling correction.
    - `tf_idf.py`: To perform tf-idf ranking for free text query search.
    - `rocchio.py`: Unused file that implements Relevance Feedback.
    - `boolean.py`: To perform Standard Boolean retrieval and Extended Boolean retrieval.
    - `extended_boolean.py`: Implements the Extended Boolean P-Norm algorithm for query-document similarity.
- Miscellaneous:
    - `util.py`: Helper functions for preprocessing, formatting, performing intersections.
    - `dictionary.txt`: To store the index dictionary of the collection.
    - `postings.txt`: To store the positional index posting lists (not in this repo due to large size ~700MB).
    - `spellchecker/`: pyspellcheck library files for spelling correction.
- Documentation:
    - `README.md`: Overview of the system.
    - `Techniques.docx`: File containing details about our experiments with query refinement.

## References

- Google, StackOverflow, GeeksForGeeks, Python docs: for Python syntax and errors
- [StackOverflow](https://stackoverflow.com/questions/53062137/key-function-for-heapq-nlargest): For getting most relevant documents in right order using heapq
- [NLTK documentation](https://www.nltk.org/): usage of functions like tokenize, PorterStemmer, WordNet, WSD
- [linecache documentation](https://docs.python.org/3/library/linecache.html): usage of getline function
- Introduction to Information Retrieval textbook: For algorithms like TFxIDF scoring for free text queries, Positional intersect, and Intersection of postings lists.
- [Information Retrieval: Data Structures & Algorithms](http://dns.uls.cl/~ej/daa_08/Algoritmos/books/book5/chap15.htm) book: Extended Boolean models and the P-norm model.
- [Pyspellcheck](https://pypi.org/project/pyspellchecker/): Library to perform spelling correction operations
- [Rocchio algorithm](https://nlp.stanford.edu/IR-book/html/htmledition/rocchio-classification-1.html): For pseudo relevance feedback for query refinement
