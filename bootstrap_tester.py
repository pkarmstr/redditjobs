__author__ = 'keelan'

import unittest
import json
import numpy
from bootstrap_pipeline import nested_tokenize, postprocess_tokenized_text, MutualBootStrapper

class BootStrapTester(unittest.TestCase):

    def setUp(self):
        self.all_data = json.load(open("comment_data/jobs-1.json"))
        self.slash_word = "60,000/yr"
        self.data = map(nested_tokenize, ["I am a lawyer", "I am a doctor",
                                          "I work as a lawyer", "I became a doctor",
                                          "I am a nun"])
        self.seeds = ["doctor", "lawyer"]
        self.mbs = MutualBootStrapper(self.data, self.seeds)
        self.mbs.find_patterns()
        self.mbs.set_counter_arrays()
        self.mbs.find_seeds()
        self.pattern_index = self.mbs.pattern_alphabet.get_index(("am", "a", "<x>"))

    def test_nested_tokenize(self):
        single_sent = nested_tokenize(self.all_data["cfy2a30"])
        self.assertEqual(len(single_sent), 1)
        self.assertGreater(len(single_sent[0]), 1)
        multi_sents = nested_tokenize(self.all_data["cfy9b0t"])
        self.assertGreater(len(multi_sents), 1)

    def test_postprocess_tokenized(self):
        nested = [[self.slash_word]]
        postprocess_tokenized_text(nested)
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

if __name__ == "__main__":
    unittest.main()
