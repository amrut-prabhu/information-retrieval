# N-gram Language Models for Text Classification

## Usage

```sh
python build_test_LM.py -b input-file-for-building-LM -t input-file-for-testing-LM -o output-file

# Example
python build_test_LM.py -b input.train.txt -t input.test.txt -o input.out.txt
```

To run the script to test on the validation data set:

```sh
python build_validation_LM.py -b input.train.txt -t input.validation.txt -o input.out.txt
```

## Evaluation

```sh
python eval.py file-containing-your-results file-containing-correct-results

# Example
python eval.py input.out.txt input.correct.txt
```

## Approach

### Building the LM (`build_LM()`):

The first part of building the LM is to get the counts of occurrences of ngrams from the training sentences for each of the 3 languages - malaysian, indonesian and tamil. 
For each sentence of length `len`, `len - 4 + 1` ngrams  are derived from it and the count of that ngram for the specified language  is incremented. 

Add-one smoothing is also performed so that all 3 languages have the same dictionary.

The counts of the ngrams in each language are then normalised (using the number of tokens counted for that language) to represent the counts as probabilities.

### Classifying using the LM (`test_LM()`):

A sentence is classified as belonging to one of the 3 languages based on the  probability of the sentence occurring in that language. 
This is calculated by  multiplying the probabilities of ngrams with non-zero probabilities in that sentence for each language, and ignoring out-of-vocabulary ngrams. 

In order to prevent the probability from becoming very small and resulting in an underflow due to repeated multiplication of values less than or equal to 1, I sum up the log of the probabilities instead.

The sentence is then classified as the language that assigned the highest probability value for that sentence. 

In order to classify a sentence as "other", I checked whether the percentage of known ngrams in the sentence was below a certain threshold. 
The value of the threshold is set to 0.55 (i.e. 45% of ngrams are out-of-vocabulary). 
This value was decided based on heuristics and some testing using a validation data set (`build_validation_LM.py` and `input.validation.txt`). 
The validation data consists of sentences belonging to similar languages (classified as "other") like Tagalog, Telegu, and Malayalam.

## File descriptions

- `build_test_LM.py`: Creates the language model from the training data, and then writes the predicted outputs of the test data to the output file.

- `build_validation_LM.py`: Provided for reference. Used to decide on a suitable value for the threshold to determine classification as "other".

- `input.validation.txt`: Provided for reference. Consists of test sentences and some from similar languages, classified as "other"

Use `python build_test_LM.py -b input.train.txt -t input.test.txt -o input.out.txt` to run the language model.

Use `python build_validation_LM.py -b input.train.txt -t input.validation.txt -o input.out.txt` to run the validation set script.
