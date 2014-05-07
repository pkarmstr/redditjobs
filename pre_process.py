__author__ = 'keelan'

import cPickle
import nltk
import re
import json
import os
from opennlp_wrapper import OpenNLPChunkerWrapper, Chunk

chunker = OpenNLPChunkerWrapper("/home/keelan/lib/apache-opennlp-1.5.3/bin/opennlp", \
                                             "/home/keelan/lib/en-chunker.bin")

def chunk_data(pos_tagged_data):
    print "chunking... ",
    chunked = []
    for entry in pos_tagged_data:
        new_sentence = []
        for sentence in entry:
            chunks = chunker.chunk_sent(sentence)
            new_sentence.append(chunks)
        chunked.append(new_sentence)
    print "[DONE]"
    return chunked

def tokenize(text):
    print "tokenizing...",
    all_entries = []
    for entry in text:
        tokenized_entry = _nested_tokenize(entry)
        all_entries.append(tokenized_entry)
    print "[DONE]"
    return all_entries

def _nested_tokenize(untokenized_sentences):
    tokenized_sents = nltk.sent_tokenize(untokenized_sentences)
    tokenized_words = [nltk.word_tokenize(sent) for sent in tokenized_sents]
    return _postprocess_tokenized_text(tokenized_words)

def _postprocess_tokenized_text(tokenized):
    better = []
    for i,sent in enumerate(tokenized):
        new_sentence = []
        for j,word in enumerate(sent):
            tokenized[i][j] = word.lower()
            if word == "[":
                input = ["-LRB-"]
            elif word == "]":
                input = ["-LLB-"]
            elif "/" in word:
                input = re.sub(r"/", r" / ", word).split()
            else:
                input = [word]
            new_sentence.extend(input)
        better.append(new_sentence)
    return better

def pos_tag(tokenized_data):
    print "POS tagging... ",
    pos_tagged_data = []
    for entry in tokenized_data:
        new_entry = []
        for sentence in entry:
            tagged = nltk.pos_tag(sentence)
            new_entry.append(tagged)
        pos_tagged_data.append(new_entry)
    print "[DONE]"
    return pos_tagged_data

def read_all_data(data_dir):
    files = os.listdir(data_dir)
    all_data = {}
    for f in files:
        with open(os.path.join(data_dir, f), "r") as f_in:
            json_data = json.load(f_in)
            all_data.update(json_data)

    return all_data

def save_all_data(data, filepath):
    with open(filepath, "w") as f_out:
        json.dump(data, f_out, indent=4)

def stringify_data(data):
    print "turning into strings... ",
    output = []
    for entry in data:
        new_sentences = []
        for sentence in entry:
            sentence_str = ["<START>_<START>"]
            for blob in sentence:
                if isinstance(blob, Chunk):
                    sentence_str.append(str(blob))
                else:
                    sentence_str.append("_".join(blob))
            new_sentences.append(" ".join(sentence_str))
        output.append(new_sentences)
    print "[DONE]"
    return output

def process(data_dir, outfile):
    json_dict = read_all_data(data_dir)
    keys,data = zip(*json_dict.items())
    print "processing {:d} entries".format(len(data))
    tokens = tokenize(data)
    pos_tagged = pos_tag(tokens)
    with open("resources/pos_tagged.pkl", "wb") as f_out:
        cPickle.dump(zip(keys,pos_tagged), f_out)
    chunked_data = chunk_data(pos_tagged)
    str_data = stringify_data(chunked_data)
    if len(str_data) != len(keys):
        raise ValueError("{:d} != {:d}".format(len(str_data), len(keys))
    final_data = dict(zip(keys, str_data))
    print "saving... ",
    save_all_data(final_data, outfile)
    print "[DONE]"

if __name__ == "__main__":
    process("comment_data", "resources/prepared_data.json")
