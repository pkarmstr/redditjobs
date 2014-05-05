__author__ = 'keelan'

import nltk
import json

def nested_tokenize(untokenized_sentences):
    tokenized_sents = nltk.sent_tokenize(untokenized_sentences)
    return [nltk.word_tokenize(sent) for sent in tokenized_sents]

if __name__ == "__main__":
    all_data = json.load(open("comment_data/jobs-1.json"))
    print nested_tokenize(all_data["cfy2a30"])