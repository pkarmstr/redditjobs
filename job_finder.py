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

submissions = ["http://www.reddit.com/r/AskReddit/comments/1ao38p/do_you_have_a_job_that_the_average_person_doesnt/",
               "http://www.reddit.com/r/AskReddit/comments/1nnuv6/what_is_your_job_and_how_can_i_a_regular_guy_make/",
               "http://www.reddit.com/r/AskReddit/comments/l1tb5/who_actually_enjoys_their_job_what_do_you_do_what/",
               "http://www.reddit.com/r/AskReddit/comments/oywrl/what_are_some_not_so_well_known_but_common_and/",
               "http://www.reddit.com/r/AskReddit/comments/1erbxo/what_are_some_jobs_that_pay_well_and_do_not/",
               "http://www.reddit.com/r/AskReddit/comments/fwdb3/maybe_an_odd_question_but_what_exactly_are_these/",
               "http://www.reddit.com/r/AskReddit/comments/176vgf/what_jobs_baffle_you_in_the_fact_that_they_exist/",
               "http://www.reddit.com/r/AskReddit/comments/zctye/does_anyone_love_their_job_if_so_what_do_you_do/"]

user_agent = "scraping job info from reddit for science"

start = time.time()

r = praw.Reddit(user_agent)


file_i = 1 # already got jobs-1
num_comments = 1

for submission in submissions:
    try:
        jobs_submission = r.get_submission(submission)
    except:
        continue

    all_comments = jobs_submission.comments
    all_comments_body = {}
    more_comments = True

    while more_comments:
        more_comments = False
        for c in all_comments:
            try:
                try:
                    all_comments_body[c.id] = c.body
                    num_comments += 1

                except AttributeError, e:
                    # we've hit a MoreComments object, no `body` attribute
                    all_comments = c.comments()
                    more_comments = True
            except:
                continue

            if num_comments%5000 == 0 and all_comments_body:
                # occasionally, MoreComments.comments() doesn't return anything?
                # save every 1000 comments into a separate file
                file_i += 1
                outfile = join(basedir, "jobs-{:d}.json".format(file_i))
                with open(outfile, "w") as f_out:
                    f_out.write(json.dumps(all_comments_body, indent=4))
                all_comments_body = {} # clear our "cache" of comments

if all_comments_body:
    # save anything to disk we have left over
    file_i += 1
    outfile = join(basedir, "jobs-{:d}.json".format(file_i))
    with open(outfile, "w") as f_out:
        f_out.write(json.dumps(all_comments_body, indent=4))


with open("jobs_scraper.log", "a") as f_out:
    f_out.write("wrote to {:d} files\n".format(file_i))
    f_out.write("saved {:d} comments\n".format(num_comments))
    f_out.write("time took scraping was {:f} seconds\n".format(time.time()-start))
