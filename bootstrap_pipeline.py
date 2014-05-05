__author__ = 'keelan'

import nltk
import json
import re
import numpy
from helper import Alphabet
from collections import defaultdict

def nested_tokenize(untokenized_sentences):
    tokenized_sents = nltk.sent_tokenize(untokenized_sentences)
    tokenized_words = [nltk.word_tokenize(sent) for sent in tokenized_sents]
    postprocess_tokenized_text(tokenized_words)
    return tokenized_words

def postprocess_tokenized_text(tokenized):
    for i,sent in enumerate(tokenized):
        for j,word in enumerate(sent):
            tokenized[i][j] = word.lower()
            if "/" in word:
                tokenized[i][j] = re.sub(r"/", r" / ", word)
                #mutating the list

class MutualBootStrapper:

    def __init__(self, tokenized_data, seeds, patterns=None):
        self.tokenized_data = tokenized_data
        self.seeds = set(seeds)
        self.pattern_alphabet = Alphabet()
        if patterns is not None:
            for p in patterns:
                self.pattern_alphabet.add(p)
        self.candidate_seeds = defaultdict(set)
        self.n_pattern_array = None
        self.f_pattern_array = None
        self.first_pattern_words = set()

    def build_patterns(self, sentence, index, size):
        window_start = index-size
        window_end = index+1
        sentence_copy = list(sentence)
        sentence_copy[index] = "<x>"
        while window_start <= index: # this isn't quite right
            candidate = sentence_copy[window_start:window_end]
            if len(candidate) > 1:
                self.pattern_alphabet.add(tuple(candidate))
                if candidate[0] != "<x>":
                    self.first_pattern_words.add(candidate[0])
                else:
                    self.first_pattern_words.add(candidate[1])
            window_start += 1
            window_end += 1

    def find_patterns(self):
        for entry in self.tokenized_data:
            for sentence in entry:
                for i,word in enumerate(sentence):
                    if word in self.seeds:
                        self.build_patterns(sentence, i, 2)
                        self.build_patterns(sentence, i, 1)

    def set_counter_arrays(self):
        self.n_pattern_array = numpy.ones(self.pattern_alphabet.size())
        self.f_pattern_array = numpy.ones(self.pattern_alphabet.size())

        # if not self.n_pattern_array or not self.f_pattern_array:
        #     self.n_pattern_array = new_n_array
        #     self.f_pattern_array = new_f_array
        # else:
        #     new_n_array[0:self.n_pattern_array.size] = self.n_pattern_array
        #     self.n_pattern_array = new_n_array
        #     new_f_array[0:self.f_pattern_array.size] = self.f_pattern_array
        #     self.f_pattern_array = new_f_array

    def find_seeds(self):
        for entry in self.tokenized_data:
            for sentence in entry:
                for i in range(len(sentence)):
                    if sentence[i] in self.first_pattern_words:
                        self.match_pattern(sentence, i, 3)
                        self.match_pattern(sentence, i, 2)

    def match_pattern(self, sentence, index, size):
        window_start = index-1
        window_end = index+size-1
        window = sentence[window_start:window_end]
        for seed_candidate_index in range(len(window)):
            window_copy = list(window)
            window_copy[seed_candidate_index] = "<x>"
            pattern = tuple(window_copy)
            if len(pattern) > 1 and self.pattern_alphabet.has_label(pattern):
                candidate_seed = window[seed_candidate_index]
                pattern_index = self.pattern_alphabet.get_index(pattern)

                # increment our counters
                self.n_pattern_array[pattern_index] += 1
                if candidate_seed not in self.seeds:
                    self.f_pattern_array[pattern_index] += 1

                    # update our candidate seeds
                    self.candidate_seeds[candidate_seed].add(pattern_index)

    def calculate_pattern_scores(self):
        self.pattern_scores = (self.f_pattern_array/self.n_pattern_array)*numpy.log2(self.f_pattern_array)

    def calculate_seed_scores(self):
        self.candidate_seed_scores = {}
        for candidate_seed,matched_patterns_set in self.candidate_seeds.iteritems():
            matched_patterns = list(matched_patterns_set)
            score = numpy.sum((self.pattern_scores[matched_patterns] * 0.01) + 1)
            self.candidate_seed_scores[candidate_seed] = score

    def cull_candidates(self):
        self.calculate_pattern_scores()
        self.calculate_seed_scores()
        sorted_candidates = sorted([(v,k) for k,v in self.candidate_seed_scores.iteritems()], reverse=True)
        return zip(*sorted_candidates)[1][:5]

    def clear_data(self):
        self.candidate_seeds = defaultdict(set)

    def run_iteration(self):
        self.find_patterns()
        self.set_counter_arrays()
        self.find_seeds()
        best_five = self.cull_candidates()
        self.seeds.update(best_five)
        self.clear_data()

    def run(self, num_iterations=50):
        for i in range(num_iterations):
            print "Iteration: {:d}".format(i+1)
            self.run_iteration()
            print "number of seed terms: {:d}".format(len(self.seeds))
            print "number of total patterns: {:d}".format(self.pattern_alphabet.size())
            print "\n"

    def save_seeds(self, outfile):
        with open(outfile, "w") as f_out:
            f_out.write("\n".join(self.seeds))

    def save_patterns(self, outfile):
        with open(outfile, "w") as f_out:
            f_out.write()

if __name__ == "__main__":
    pass