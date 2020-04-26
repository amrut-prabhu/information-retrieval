from collections import defaultdict
from spellchecker import SpellChecker

from nltk.corpus import wordnet
from nltk.wsd import lesk

import math

import util

def query_expansion_thesaurus(query_str):
    """
    Params:
        - query_str: Original input query string

    Returns:
        - new_query: List of expanded query terms and weights [ (term, weight), ...]
    """

    query_str = query_str.replace('AND', '').replace('"', '')
    query_terms = set([query_term.strip() for query_term in query_str.split(' ')])

    term_weights = defaultdict(lambda: 0.0)
    new_query_terms = list(query_terms)

    ORIGINAL_TERM_WEIGHT = 1
    SYNONYM_TERM_WEIGHT = 0.5
    MISSPELLING_TERM_WEIGHT = 0.6
    CONTEXT_TERM_WEIGHT = 0.7


    for term in query_terms:
        term_weights[term] = ORIGINAL_TERM_WEIGHT


    # Add synonyms to query
    FRACTION_SYNONYMS = 0.35

    synonyms = []
    for term in query_terms:
        for syn in wordnet.synsets(term):
            num_synonyms = math.ceil(len(syn.lemmas()) * FRACTION_SYNONYMS)

            for l in syn.lemmas()[:num_synonyms]:
                for t in l.name().split("_"):
                    synonyms.append(t)
                    term_weights[t] = max(SYNONYM_TERM_WEIGHT, term_weights[t])

        # Use original query context to find suitable synonyms
        context_syn = lesk(query_str, term)
        if context_syn is not None:
            for l in context_syn.lemmas():
                for t in l.name().split("_"):
                    synonyms.append(t)
                    term_weights[t] = max(CONTEXT_TERM_WEIGHT, term_weights[t])

    new_query_terms.extend(synonyms)


    # Add spelling corrections
    spell = SpellChecker()

    unknown_misspelled_terms = spell.unknown(query_terms)
    for term in unknown_misspelled_terms:
        new_query_terms.append(spell.correction(term))  # Add the most likely correct word

    known_misspelled_terms = spell.known(query_terms)
    for mispelled_term in known_misspelled_terms:
        corrected_terms = spell.known(spell.edit_distance_2(mispelled_term))

        probs = []
        for term in corrected_terms:
            probs.append((term, spell.word_probability(term)))

        probs = sorted(probs, key=lambda x: x[1], reverse=True)
        new_corrected_terms = [term[0] for term in probs]

        new_query_terms.extend(new_corrected_terms[:3])  # Add top 3 corrections
        for t in new_corrected_terms[:3]:
            term_weights[t] = max(MISSPELLING_TERM_WEIGHT, term_weights[t])


    # Preprocess terms and assign weights to the expanded query terms
    new_query = defaultdict(lambda: 0.0)
    for term in set(new_query_terms):
        for new_term in set(util.preprocess_content(term)):
            new_query[new_term] = max(term_weights[term], new_query[new_term])

    new_query = [(term, weight) for term, weight in new_query.items()]

    return new_query

