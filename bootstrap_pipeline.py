__author__ = 'keelan'

import nltk
import json
import re
import numpy
from helper import Alphabet
from opennlp_wrapper import Chunk
from collections import defaultdict

def read_newline_file(input_file):
    all_lines = []
    with open(input_file, "r") as f_in:
        for line in f_in:
            line = line.rstrip()
            all_lines.append(line)
    return all_lines

class MutualBootStrapper:

    def __init__(self, data, seeds, patterns=None, processing=1):
        if processing == 0:
            tokenized = self.tokenize(data)
            self.pos_tagged_data = self.pos_tag(tokenized)
            self.find_patterns = self.find_patterns_tagged
            self.find_seeds = self.find_seeds_tagged
        elif processing == 1:
            self.chunked_data = data
            self.find_patterns = self.find_patterns_chunked
            self.find_seeds = self.find_seeds_chunked
        self.permanent_lexicon = set(seeds)
        self.temporary_lexicon = defaultdict(set)
        for s in seeds:
            self.temporary_lexicon[s] = set()
        self.best_extraction_patterns = set()
        self.pattern_alphabet = Alphabet()
        if patterns is not None:
            for p in patterns:
                self.pattern_alphabet.add(p)
        self.n_counter_sets = None # import for getting candidate seeds
        self.f_counter_sets = None
        self.n_pattern_array = None
        self.f_pattern_array = None
        self.first_pattern_words = set()

    def tokenize(self, text):
        print "tokenizing...",
        all_entries = []
        for entry in text:
            tokenized_entry = self._nested_tokenize(entry)
            all_entries.append(tokenized_entry)
        print "[DONE]"
        return all_entries

    def _nested_tokenize(self, untokenized_sentences):
        tokenized_sents = nltk.sent_tokenize(untokenized_sentences)
        tokenized_words = [nltk.word_tokenize(sent) for sent in tokenized_sents]
        self._postprocess_tokenized_text(tokenized_words)
        return tokenized_words

    def _postprocess_tokenized_text(self, tokenized):
        for i,sent in enumerate(tokenized):
            for j,word in enumerate(sent):
                tokenized[i][j] = word.lower()
                if "/" in word:
                    tokenized[i][j] = re.sub(r"/", r" / ", word)
                    #mutating the list

    def pos_tag(self, tokenized_data):
        print "POS tagging... ",
        pos_tagged_data = []
        for entry in tokenized_data:
            new_entry = []
            for sentence in entry:
                tagged = [("<START>", "<START>")]
                tagged.extend(nltk.pos_tag(sentence))
                new_entry.append(tagged)
            pos_tagged_data.append(new_entry)
        print "[DONE]"
        return pos_tagged_data

    def build_patterns_tagged(self, sentence, index, size):
        window_start = index-size
        window_end = index+1
        sentence_copy = list(sentence)
        sentence_copy[index] = "<x>",
        while window_start <= index: # this isn't quite right
            try:
                candidate = zip(*sentence_copy[window_start:window_end])[0]
            except IndexError:
                candidate = []
            if len(candidate) > 1:
                self.pattern_alphabet.add(tuple(candidate))
                if candidate[0] != "<x>":
                    self.first_pattern_words.add(candidate[0])
                else:
                    self.first_pattern_words.add(candidate[1])
            window_start += 1
            window_end += 1

    def find_patterns_tagged(self):
        for entry in self.pos_tagged_data:
            for sentence in entry:
                for i,(word,tag)  in enumerate(sentence):
                    if word in self.temporary_lexicon:
                        self.build_patterns_tagged(sentence, i, 2)
                        self.build_patterns_tagged(sentence, i, 1)

    def find_patterns_chunked(self):
        for entry in self.chunked_data:
            for sentence in entry:
                for i,word in enumerate(sentence):
                    if isinstance(word, Chunk) and word.head in self.temporary_lexicon:
                        self.build_patterns_chunked(sentence, i, 2)
                        self.build_patterns_chunked(sentence, i, 1)

    def build_patterns_chunked(self, sentence, index, size):
        sentence_copy = list(sentence)
        sentence_copy[index] = "<x>",
        sentence_copy = self._flatten_chunks(sentence_copy)
        index = sentence_copy.index("<x>")
        window_start = index-size
        window_end = index+1
        while window_start <= index:
            candidate = sentence_copy[window_start:window_end]
            if len(candidate) > 1:
                self.pattern_alphabet.add(tuple(candidate))
            window_start += 1
            window_end += 1

    def _flatten_chunks(self, sentence):
        flattened_sentence = []
        for constituent in sentence:
            if isinstance(constituent, Chunk):
                flattened_sentence.extend(constituent.tokens)
            else:
                flattened_sentence.append(constituent[0])
        return flattened_sentence

    def set_counter_arrays(self):
        tmp_lst = [[]] * self.pattern_alphabet.size() # must be careful about pointers here
        self.n_counter_sets = map(set, tmp_lst)
        self.f_counter_sets = map(set, tmp_lst)

    def find_seeds_chunked(self):
        for entry in self.chunked_data:
            for sentence in entry:
                for i in range(len(sentence)):
                    if isinstance(sentence[i], Chunk):
                        self.match_pattern_chunked(sentence, i, 2)
                        self.match_pattern_chunked(sentence, i, 1)

    def match_pattern_chunked(self, sentence, index, size):
        candidate_seed = sentence[index].head
        sentence_copy = list(sentence)
        sentence_copy[index] = "<x>",
        sentence_copy = self._flatten_chunks(sentence_copy)
        index = sentence_copy.index("<x>")
        window_start = index-size
        window_end = index+1
        while window_start <= index:
            window = sentence_copy[window_start:window_end]
            pattern = tuple(window)
            if len(pattern) > 1 and \
                    self.pattern_alphabet.has_label(pattern) and \
                    len(candidate_seed) > 2:

                pattern_index = self.pattern_alphabet.get_index(pattern)

                # increment our counters
                self.n_counter_sets[pattern_index].add(candidate_seed)
                if candidate_seed not in self.temporary_lexicon:
                    self.f_counter_sets[pattern_index].add(candidate_seed)

            window_start += 1
            window_end += 1

    def find_seeds_tagged(self):
        for entry in self.pos_tagged_data:
            for sentence in entry:
                for i in range(len(sentence)):
                    if sentence[i][0] in self.first_pattern_words:
                        self.match_pattern_tagged(sentence, i, 3)
                        self.match_pattern_tagged(sentence, i, 2)

    def match_pattern_tagged(self, sentence, index, size):
        window_start = index-1
        window_end = index+size-1
        window = sentence[window_start:window_end]
        for seed_candidate_index in range(len(window)):
            window_copy = list(window)
            _,pos = window_copy[seed_candidate_index]
            window_copy[seed_candidate_index] = ("<x>", pos)
            pattern = tuple(zip(*window_copy)[0])
            if len(pattern) > 1 and \
                    self.pattern_alphabet.has_label(pattern) and \
                    window[seed_candidate_index][1].startswith("NN") and \
                    len(window[seed_candidate_index][0]) > 2:

                candidate_seed = window[seed_candidate_index][0]
                pattern_index = self.pattern_alphabet.get_index(pattern)

                # increment our counters
                self.n_counter_sets[pattern_index].add(candidate_seed)
                if candidate_seed not in self.temporary_lexicon:
                    self.f_counter_sets[pattern_index].add(candidate_seed)

    def calculate_pattern_scores(self):
        self.n_pattern_array = numpy.array(map(len, self.n_counter_sets), dtype=float) + 1.
        self.f_pattern_array = numpy.array(map(len, self.f_counter_sets), dtype=float) + 1.

        self.pattern_scores = numpy.nan_to_num((self.f_pattern_array/self.n_pattern_array)*numpy.log2(self.f_pattern_array))

    def calculate_seed_scores(self):
        self.candidate_seed_scores = {}
        for candidate_seed,matched_patterns_set in self.temporary_lexicon.iteritems():
            matched_patterns = list(matched_patterns_set)
            score = numpy.sum((self.pattern_scores[matched_patterns] * 0.01) + 1)
            #print score
            self.candidate_seed_scores[candidate_seed] = score

    def cull_candidates(self):
        self.calculate_pattern_scores()
        self.calculate_seed_scores()
        sorted_candidates = sorted([(v,k) for k,v in self.candidate_seed_scores.iteritems()], reverse=True)
        #print sorted_candidates
        try:
            return zip(*sorted_candidates)[1][:5]
        except IndexError:
            return []

    def run_mutual_bootstrapping(self):
        added_patterns = 0
        best_score = 5
        while added_patterns < 10 or best_score > 1.8:
            self.find_patterns()
            self.set_counter_arrays()
            self.find_seeds()
            self.calculate_pattern_scores()

            best_pattern_index = numpy.nanargmax(self.pattern_scores)
            while best_pattern_index in self.best_extraction_patterns:
                self.pattern_scores[best_pattern_index] = -10000000.
                best_pattern_index = numpy.nanargmax(self.pattern_scores)

            if self.pattern_scores[best_pattern_index] < 0.7:
                return

            best_score = self.pattern_scores[best_pattern_index]
            #print best_score, self.pattern_alphabet.get_label(best_pattern_index)

            self.best_extraction_patterns.add(best_pattern_index)
            for seed in self.n_counter_sets[best_pattern_index]:
                self.temporary_lexicon[seed].add(best_pattern_index)
            added_patterns += 1

    def run_meta_bootstrapping(self):
        best_five = self.cull_candidates()
        self.permanent_lexicon.update(best_five)
        self.temporary_lexicon = defaultdict(set)
        for s in self.permanent_lexicon:
            self.temporary_lexicon[s] = set()

    def run(self, num_iterations=50):
        for i in range(num_iterations):
            print "Iteration: {:d}".format(i+1)
            print "running mutual bootstrapping..."
            self.run_mutual_bootstrapping()
            print "[DONE]"
            print "running meta bootstrapping...",
            self.run_meta_bootstrapping()
            print "[DONE]"
            print "number of seed terms: {:d}".format(len(self.permanent_lexicon))
            print "number of total patterns: {:d}".format(self.pattern_alphabet.size())
            print "\n"


    def save_seeds(self, outfile):
        with open(outfile, "w") as f_out:
            f_out.write("\n".join(s.encode("utf-8") for s in self.permanent_lexicon))

    def save_patterns(self, outfile):
        with open(outfile, "w") as f_out:
            patterns = []
            for pattern_index in self.best_extraction_patterns:
                patterns.append(" ".join(self.pattern_alphabet.get_label(pattern_index)))
            f_out.write("\n".join(s.encode("utf-8") for s in patterns))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("json_data", help="a set of data instances in a json format")
    parser.add_argument("seeds", help="newline separated text file containing seed terms")
    parser.add_argument("-n", "--num_iterations", type=int)
    parser.add_argument("-p", "--prefix", help="file name prefix when saving to disk")
    parser.add_argument("--patterns", help="list of patterns to begin with")
    parser.add_argument("-t", "--tokenize", help="use chunks or not")

    all_args = parser.parse_args()
    raw_data = [v for k,v in json.load(open(all_args.json_data)).iteritems()]

    all_data = []
    for entry in raw_data:
        new_entry = []
        for sentence in entry:
            new_sentence = Chunk.chunked_str_to_list(sentence)
            new_entry.append(new_sentence)
        all_data.append(new_entry)

    seeds = read_newline_file(all_args.seeds)

    if all_args.patterns:
        patterns = read_newline_file(all_args.patterns)
    else:
        patterns = None

    if all_args.tokenize:
        proc = int(all_args.tokenize)
    else:
        proc = 1

    mbs = MutualBootStrapper(all_data, seeds, patterns, processing=proc)
    mbs.run(all_args.num_iterations)

    file_prefix = all_args.prefix

    mbs.save_seeds("{:s}-new-seeds.txt".format(file_prefix))
    mbs.save_patterns("{:s}-new-patterns.txt".format(file_prefix))

    print "saved everything"

