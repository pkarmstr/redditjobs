__author__ = 'keelan'

import os
import re
import json
import wikitools
import time

url_files = os.listdir("wiki-stuff/urls/")
base_url = "http://en.wikipedia.org/w/api.php?action=query&prop=revisions&rvprop=content&format=json&&titles="

for f in url_files:
    print f
    page_names = []
    with open("wiki-stuff/urls/"+f, "r") as f_in:
        for line in f_in:
            line = line.split("\t")[0]
            page_title = re.sub(r"\s", r"_", line)
            page_names.append(page_title)
    new_url = "|".join(page_names)
    resp = wikitools.urllib.urlopen(base_url+new_url)
    all_data = json.loads(resp.read())
    pages_and_titles = {}
    for k in all_data["query"]["pages"].keys():
        try:
            title = all_data["query"]["pages"][k]["title"]
            content = all_data["query"]["pages"][k]["revisions"][0]["*"]
            pages_and_titles[title] = content
        except:
            continue
    category = f[:-9]
    with open("wiki-stuff/{:s}.json".format(category), "w") as f_out:
        json.dump(pages_and_titles, f_out)
    time.sleep(5)

print "done"