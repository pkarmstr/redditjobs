import sys
import wikitools
from bs4 import BeautifulSoup
import re

def has_link(tag):
    return tag.name == "a" and tag.has_attr("href") and tag["href"].startswith("/wiki/")

sublists = ["http://en.wikipedia.org/wiki/List_of_computer_occupations",
            "http://en.wikipedia.org/wiki/List_of_scientific_occupations",
            "http://en.wikipedia.org/wiki/List_of_artistic_occupations",
            "http://en.wikipedia.org/wiki/List_of_dance_occupations",
            "http://en.wikipedia.org/wiki/List_of_theatre_personnel",
            "http://en.wikipedia.org/wiki/List_of_writing_occupations",
            "http://en.wikipedia.org/wiki/List_of_healthcare_occupations",
            "http://en.wikipedia.org/wiki/List_of_mental_health_occupations",
            "http://en.wikipedia.org/wiki/List_of_nursing_specialties",
            "http://en.wikipedia.org/wiki/List_of_industrial_occupations",
            "http://en.wikipedia.org/wiki/List_of_metalworking_occupations",
            "http://en.wikipedia.org/wiki/List_of_railway_industry_occupations",
            "http://en.wikipedia.org/wiki/List_of_sewing_occupations"]

get_list_name = re.compile(r"^.*?List_of_(.*?)$")

for page in sublists:
    print page
    req = wikitools.urllib.urlopen(page)
    data = req.read()
    parsed = BeautifulSoup(data)

    links = parsed.find_all(has_link)

    cleaner_links = []

    for l in links:
        cleaner_links.append("{:s}\t{:s}".format(l.text.encode("utf-8"), l["href"].encode("utf-8")))

    name = get_list_name.match(page).group(1)
    with open("wiki-stuff/{:s}-urls.txt".format(name), "w") as f_out:
        f_out.write("\n".join(cleaner_links))

print "done"