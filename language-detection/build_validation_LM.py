#!/usr/bin/python3

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from random import seed
from random import randint

import re
import nltk
import sys
import getopt
import math

N = 4 # number of units considered in the n-gram model

def build_LM(in_file):
    """
    build language models for each label
    each line in in_file contains a label and a string separated by a space

    Returns a dict { language: { ngram: probability of occurring } }
    """
    print('building language models...')

    LM = {
        'malaysian': {},
        'indonesian': {},
        'tamil': {},
    }

    # Number of tokens seen in each language
    numTokens = {
        'malaysian': 0,
        'indonesian': 0,
        'tamil': 0,
    }

    f = open(in_file, mode='r', encoding='utf8')

    i = -1
    for line in f:
        line = line.strip() # To remove newline characters and other whitespace characters at the left and right ends of the string
        start = line.find(' ') + 1 # Start index of the training data sentence

        language = line[:start - 1]
        sentence = line[start:]

        for i in range(len(sentence) - N + 1):
            ngram = sentence[i:i + N]
            
            for lang in numTokens:
                if ngram not in LM[lang]:
                    LM[lang][ngram] = 1 # Add-one smoothing
                    numTokens[lang] += 1
            
            LM[language][ngram] += 1

            numTokens[language] += 1

    f.close()

    # Normalise ngram counts into probabilities
    for lang in LM:
        for ngram in LM[lang]:
            LM[lang][ngram] /= numTokens[lang] 

    return LM


def validate_LM(in_file, out_file, LM):
    print("validating language models...")

    f_out = open(out_file, mode='w', encoding='utf8')

    pred_labels = ['malaysian', 'indonesian', 'tamil']

    # Test threshold values from [0, 0.90] in increments of 0.05
    for k in range(0, 90, 5):
        threshold = k / 100

        f_in = open(in_file, mode='r', encoding='utf8')
        line_num = 0

        correct_pred = 0 # Number of sentences classified correctly, using the current `threshold` value

        for line in f_in:
            line = line.strip()
            start = line.find(' ') + 1

            lang = line[:start - 1]
            sentence = line[start:]

            line_num += 1

            # Probabilities of sentence being malaysian, indonesian and tamil
            probs = [0, 0, 0] 
            num_counted = 0

            for i in range(len(sentence) - N + 1):
                ngram = sentence[i:i + N]

                for j in range(3):
                    if ngram in LM[pred_labels[j]]:
                        probs[j] += math.log(LM[pred_labels[j]][ngram]) # Use log to prevent value from being extremely small
                        num_counted += 1 

            num_ngrams_known = num_counted / len(LM) # Since they're counted multiple times (once for each of the LMs, due to smmothing)
            num_ngrams_total = i + 1
            
            if num_ngrams_known / num_ngrams_total <= threshold: 
                predicted_lang = 'other' # If lot of unknown words, predict language as "other"
            else:
                predicted_lang = pred_labels[probs.index(max(probs))] # Select the label that has highest probability


            if predicted_lang == lang:
                correct_pred += 1


            if k == 55:
                f_out.write(predicted_lang + " " + line + "\n")

                if lang == "other":
                    # See percentage of known ngrams for sentences that are actually "other" 
                    print("  known in " + str(line_num) + ": " + str(num_ngrams_known / num_ngrams_total * 100) + "%") 


        print("# correct for threshold=" + str(threshold) + ":  " + str(correct_pred))
        f_in.close()

    f_out.close()


def usage():
    print("usage: " + sys.argv[0] + " -b input-file-for-building-LM -t input-file-for-testing-LM -o output-file")

input_file_b = input_file_t = output_file = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'b:t:o:')
except getopt.GetoptError:
    usage()
    sys.exit(2)
for o, a in opts:
    if o == '-b':
        input_file_b = a
    elif o == '-t':
        input_file_t = a
    elif o == '-o':
        output_file = a
    else:
        assert False, "unhandled option"
if input_file_b == None or input_file_t == None or output_file == None:
    usage()
    sys.exit(2)

LM = build_LM(input_file_b)
validate_LM(input_file_t, output_file, LM)
