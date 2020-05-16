# c_value

import spacy
import pickle
import time
import math
import json
from tqdm import tqdm
import pandas as pd

# from pathos.multiprocessing import ProcessingPool as Pool
from multiprocessing import Pool
from spacy.matcher import Matcher
from collections import defaultdict
from multiprocessing.pool import Pool
from term_extraction import TermExtraction, add_term_extraction_method

start_ = 0
tmp = 0
# TOTAL_WORK = 27768
# success = 27768
# pbar = tqdm(total=27768)


def start():
    global start_
    start_ = time.time()


def end():
    global start_
    print(time.time() - start_)


# nlp = spacy.load("en_core_web_sm")
nlp = spacy.load("en_core_web_sm", parser=False, entity=False)
matcher = Matcher(nlp.vocab)
MAX_WORD_LENGTH = 6
THRESHOLD = 0
noun, adj, verb, prep, det = (
    {"POS": "NOUN", "IS_PUNCT": False},
    {"POS": "ADJ"},
    {"POS": "VERB"},
    {"POS": "ADP"},
    {"POS": "DET"},
)
patterns1 = [
    [noun],
    [adj],
    [adj, noun],
    [noun, noun],
    [noun, prep, noun],
    [noun, det, noun],
    [verb],
    [adj, adj, noun],
]
patterns2 = [
    [{"POS": {"IN": ["ADJ", "NOUN"]}, "OP": "+", "IS_PUNCT": False}, noun],
    [
        {"POS": {"IN": ["ADJ", "NOUN"]}, "OP": "*", "IS_PUNCT": False},
        noun,
        prep,
        {"POS": {"IN": ["ADJ", "NOUN"]}, "OP": "*", "IS_PUNCT": False},
        noun,
    ],
]
patterns3 = [[{"POS": {"IN": ["ADJ", "NOUN"]}, "OP": "+", "IS_PUNCT": False}, noun]]
patterns4 = [
    [{"POS": "NOUN", "OP": "+", "IS_PUNCT": False}, {"POS": "NOUN", "IS_PUNCT": False}]
]


def word_length(string):
    return string.count(" ") + 1


def helper_get_subsequences(s):
    sequence = s.split()
    if len(sequence) <= 2:
        return []
    answer = []
    for left in range(len(sequence) + 1):
        for right in range(left + 1, len(sequence) + 1):
            if left == 0 and right == len(sequence):
                continue
            answer.append(" ".join(sequence[left:right]))
    return answer


def term_counts(document, patterns=patterns4):
    term_counter = defaultdict(int)

    def add_to_counter(matcher, doc, i, matches):
        match_id, start, end = matches[i]
        candidate = str(doc[start:end])
        if word_length(candidate) <= MAX_WORD_LENGTH:
            term_counter[candidate] += 1

    for i, pattern in enumerate(patterns):
        matcher.add("term{}".format(i), add_to_counter, pattern)

    doc = nlp(document, disable=["parser", "ner"])

    matches = matcher(doc)
    return term_counter


@add_term_extraction_method
def c_values(
    technical_corpus,
    smoothing=0.01,
    verbose=False,
    have_single_word=False,
    technical_counts=None,
):

    if technical_counts is None:
        term_counts = (
            TermExtraction(technical_corpus)
            .count_terms_from_documents(verbose=verbose)
            .reindex()
        )
    else:
        term_counts = technical_counts

    order = sorted(
        list(term_counts.keys()), key=TermExtraction.word_length, reverse=True
    )

    if not have_single_word:
        order = list(filter(lambda s: TermExtraction.word_length(s) > 1, order))

    # print(order)
    term_counts = term_counts[order]

    df = pd.DataFrame(
        {
            "frequency": term_counts.values,
            "times_nested": term_counts.values,
            "number_of_nested": 1,
            "has_been_evaluated": False,
        },
        index=term_counts.index,
    )

    # print(df)
    output = []
    indices = set(df.index)

    for candidate, row in tqdm(df.iterrows()):
        f, t, n, h = row
        length = word_length(candidate)
        if length == MAX_WORD_LENGTH:
            c_val = math.log(length + smoothing) * f
        else:
            c_val = math.log(length + smoothing) * f
            if h:
                c_val -= t / n
        if c_val >= THRESHOLD:
            output.append((candidate, c_val))
            nstart = time.time()  # TODO: optimize
            for substring in helper_get_subsequences(candidate):
                if substring in indices:
                    # for substring in df.index:
                    # if substring in candidate:
                    df.loc[substring, "times_nested"] += 1
                    df.loc[substring, "number_of_nested"] += f
                    df.loc[substring, "has_been_evaluated"] = True
            global tmp
            tmp += time.time() - nstart

    output.sort(key=lambda s: s[1], reverse=True)
    return output


if __name__ == "__main__":
    pkl = pickle.load(open("../data/pmc_testing.pkl", "rb"))
    print(len(pkl))
    corpus = pkl
    # print(c_values(pkl[:20], have_single_word=False))
    print(TermExtraction(pkl[:20]).c_values())
    # print(pkl[0])
