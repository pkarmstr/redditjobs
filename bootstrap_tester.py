__author__ = 'keelan'

import unittest
import json
from bootstrap_pipeline import nested_tokenize

class BootStrapTester(unittest.TestCase):

    def setUp(self):
        self.all_data = json.load(open("comment_data/jobs-1.json"))

    def test_nested_tokenize(self):
        single_sent = nested_tokenize(self.all_data["cfy2a30"])
        self.assertEquals(len(single_sent), 1)
        self.assertGreater(len(single_sent[0]), 1)
        multi_sents = nested_tokenize(self.all_data["cfy9b0t"])
        self.assertGreater(len(multi_sents), 1)

if __name__ == "__main__":
    unittest.main()
