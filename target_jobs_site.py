import json

__author__ = 'keelan'

from urllib2 import urlopen
from bs4 import BeautifulSoup
import re
import time

base_url = "http://targetjobs.co.uk/careers-advice/job-descriptions"
super_base = "http://targetjobs.co.uk"

def proper_link(tag):
    return tag.name == "a" and tag.has_attr("href") and \
           re.match(r"^/careers-advice/job-descriptions/\d+-.*", tag["href"])

def abstract(tag):
    return tag.name == "div" and tag.has_attr("class") and "abstract" in tag["class"]

resp = urlopen(base_url)
soup = BeautifulSoup(resp.read())

links = soup.find_all(proper_link)
all_links = set()

for l in links:
    all_links.add(l["href"])

# print all_links, "\n", len(all_links)

all_descr = {}

for link in all_links:
    print link
    page = urlopen(super_base+link).read()
    soup = BeautifulSoup(page)
    title = soup.find_all("title")[0].text
    title = re.sub(r"^(.*?):.*", r"\1", title)

    all_text = []
    info = soup.find_all(abstract)[0].text
    all_text.append(info)

    for tag in soup.find_all("p"):
        all_text.append(tag.text)

    all_descr[title] = "\n".join(all_text)

    time.sleep(3)

with open("job_descr/target_jobs.json", "w") as f_out:
    json.dump(all_descr, f_out)

print "done"