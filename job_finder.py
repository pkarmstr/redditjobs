"""
short script to scrape the comments from a post on reddit about people's jobs
"""

__author__ = 'keelan'

import time
import praw
import sys
import json
from os.path import join

if len(sys.argv) != 2:
    sys.exit("usage: python job_finder.py directory")

basedir = sys.argv[1]

submission  = "http://www.reddit.com/r/AskReddit/comments/1zwthi/whats_your_job_how_much_do_you_make_per_year_how/"
user_agent = "scraping job info from reddit for science"

r = praw.Reddit(user_agent)

jobs_submission = r.get_submission(submission, comment_limit=1000)

all_comments = jobs_submission.comments
all_comments_body = {}
more_comments = True
file_i = 0
num_comments = 0

start = time.time()
while more_comments:
    more_comments = False
    for c in all_comments:
        try:
            all_comments_body[c.id] = c.body
            num_comments += 1
        except AttributeError, e:
            #we've hit a MoreComments object, no `body` attribute
            all_comments = c.comments()
            file_i += 1
            outfile = join(basedir, "jobs-{:d}.json".format(file_i))
            all_comments_body = {}
            with open(outfile, "w") as f_out:
                f_out.write(json.dumps(all_comments_body))
            more_comments = True

with open("jobs_scraper.log", "w") as f_out:
    f_out.write("wrote to {:d} files\n".format(file_i))
    f_out.write("saved {:d} comments\n".format(num_comments))
    f_out.write("time took scraping was {:f} seconds\n".format(time.time()-start))
