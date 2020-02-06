#!/usr/bin/python3

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

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


def test_LM(in_file, out_file, LM):
    """
    test the language models on new strings
    each line of in_file contains a string
    you should print the most probable label for each string into out_file
    """
    print("testing language models...")

    f_in = open(in_file, mode='r', encoding='utf8')
    f_out = open(out_file, mode='w', encoding='utf8')

    pred_labels = ['malaysian', 'indonesian', 'tamil']
    for line in f_in:
        sentence = line.strip()

        count = [0, 0, 0] 

        # Probabilities of sentence being malaysian, indonesian and tamil
        probs = [0, 0, 0] 

        for i in range(len(sentence) - N + 1):
            ngram = sentence[i:i + N]

            for i in range(3):
                if ngram in LM[pred_labels[i]]:
                    probs[i] += math.log(LM[pred_labels[i]][ngram]) # Use log to prevent value from being extremely small
                    count[i] += 1

        if max(probs) == 0:
            predicted_lang = 'other'
        else:
            predicted_lang = pred_labels[probs.index(max(probs))] # Select the label that has highest probability

        f_out.write(predicted_lang + " " + line)

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
test_LM(input_file_t, output_file, LM)
