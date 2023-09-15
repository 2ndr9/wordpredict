import heapq
import itertools as it
from collections import defaultdict
from typing import Dict, List, Tuple


class WordPredict:
    def __init__(self, corpus_words: List[str], corpus_freq: List[int], alpha=0.62):
        self.valid_prefixes = []

        self.prefix_and_its_word_and_prob_tuples = (
            generate_prefix_and_its_word_and_prob_tuples(
                corpus_words, corpus_freq, alpha
            )
        )

    def update(self, new_char_list: List[str], max_candidates=6):
        """
        Params:
        - new_char_list: List of new characters, e.g., ['a', 'b', 'c']

        Returns:
        - List of candidates, e.g., ['help', 'held', 'felt', 'hell', 'hello', 'helps']
        """

        self.valid_prefixes = update_new_valid_prefixes(
            self.valid_prefixes, new_char_list, self.prefix_and_its_word_and_prob_tuples
        )

        return get_autocomplete_candidates(
            self.prefix_and_its_word_and_prob_tuples,
            self.valid_prefixes,
            max_candidates,
        )

    def reset(self):
        """Resets the list of valid prefixes."""
        self.valid_prefixes = []


# Helper functions


def generate_prefix_and_its_word_and_prob_tuples(
    corpus_words: List[str], corpus_freq: List[int], alpha: float
):
    word_freq = dict(zip(corpus_words, corpus_freq))
    prefix_and_its_word_and_prob_tuples: Dict[
        str, List[Tuple[str, float]]
    ] = defaultdict(list)

    for word, freq in word_freq.items():
        for i in range(1, len(word) + 1):
            prefix = word[:i]
            prob = (alpha ** (len(word) - i)) * freq
            prefix_and_its_word_and_prob_tuples[prefix].append((word, prob))

    # sort by probability in order to use heapq.merge
    for prefix, tuples in prefix_and_its_word_and_prob_tuples.items():
        prefix_and_its_word_and_prob_tuples[prefix] = sorted(
            tuples, key=lambda x: x[1], reverse=True
        )

    return prefix_and_its_word_and_prob_tuples


def update_new_valid_prefixes(
    old_valid_prefixes: List[str],
    new_char_list: List[str],
    prefix_and_its_word_and_prob_tuples: Dict[str, List[Tuple[str, float]]],
):
    new_prefixes = (
        new_char_list
        if len(old_valid_prefixes) == 0
        else [
            f"{valid_prefix}{new_char}"
            for valid_prefix, new_char in it.product(old_valid_prefixes, new_char_list)
        ]
    )
    new_valid_prefixes = [
        prefix
        for prefix in new_prefixes
        if prefix in prefix_and_its_word_and_prob_tuples
    ]
    return new_valid_prefixes


def get_autocomplete_candidates(
    prefix_and_its_word_and_prob_tuples: Dict[str, List[Tuple[str, float]]],
    valid_prefixes: List[str],
    max_candidates,
):
    word_and_prob_tuples = [
        prefix_and_its_word_and_prob_tuples.get(prefix, []) for prefix in valid_prefixes
    ]

    # each word_and_prob_tuple is sorted by probability, so we can use heapq.merge
    merged_sorted_tuples = list(
        heapq.merge(*word_and_prob_tuples, key=lambda x: x[1], reverse=True)
    )

    return [tuple[0] for tuple in merged_sorted_tuples[:max_candidates]]