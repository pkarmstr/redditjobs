__author__ = 'keelan'

import unittest
import json
from opennlp_wrapper import OpenNLPChunkerWrapper
from bootstrap_pipeline import MutualBootStrapper

class BootStrapTester(unittest.TestCase):

    def setUp(self):
        self.json_data = json.load(open("comment_data/jobs-1.json"))
        self.all_data = [v for k,v in self.json_data.iteritems()]
        self.slash_word = "60,000/yr"
        self.data = ["I am a lawyer.", "I am a doctor.", "I work as a lawyer.",
                     "I became a doctor.", "I am a nun."]
        self.seeds = ["doctor", "lawyer"]

        self.mbs = MutualBootStrapper(self.data, self.seeds)
        self.mbs.find_patterns()
        self.mbs.set_counter_arrays()
        self.mbs.find_seeds()
        self.pattern_index = self.mbs.pattern_alphabet.get_index(("am", "a", "<x>"))
        self.chunker = OpenNLPChunkerWrapper("/home/keelan/lib/apache-opennlp-1.5.3/bin/opennlp", \
                                             "/home/keelan/lib/en-chunker.bin")


    def test_nested_tokenize(self):
        single_sent = self.mbs._nested_tokenize(self.json_data["cfy2a30"])
        self.assertEqual(len(single_sent), 1)
        self.assertGreater(len(single_sent[0]), 1)
        multi_sents = self.mbs._nested_tokenize(self.json_data["cfy9b0t"])
        self.assertGreater(len(multi_sents), 1)

    def test_postprocess_tokenized(self):
        nested = [[self.slash_word]]
        self.mbs._postprocess_tokenized_text(nested)
        self.assertEqual(nested[0][0], "60,000 / yr")

    def test_pattern_finder(self):
        # print self.mbs.candidate_patterns
        self.assertGreater(self.mbs.pattern_alphabet.size(), 0)
        self.assertTrue(self.mbs.pattern_alphabet.has_label(("as", "a", "<x>")))

    def test_counter_arrays(self):
        self.assertGreater(self.mbs.n_pattern_array.size, 0)

    def test_find_seeds(self):
        self.assertEqual(self.mbs.n_pattern_array[self.pattern_index], 4)
        self.assertEqual(self.mbs.f_pattern_array[self.pattern_index], 2)
        self.assertTrue("nun" in self.mbs.candidate_seeds)
        self.assertTrue(self.pattern_index in self.mbs.candidate_seeds["nun"])

    def test_opennlp_chunker(self):
        tagged_sentence = [("Rockwell", "NNP"), ("said", "VBD"),
                           ("the", "DT"), ("agreement", "NN"), (".", ".")]

        chunked_sentence = self.chunker.chunk_sent(tagged_sentence)
        # print chunked_sentence
        self.assertEqual(len(chunked_sentence), 4)

if __name__ == "__main__":
    unittest.main()
