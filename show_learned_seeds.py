import sys
from bootstrap_pipeline import read_newline_file

old_seeds = sys.argv[2]
new_seeds = sys.argv[1]
outfile = sys.argv[3]

new = read_newline_file(new_seeds)
old = read_newline_file(old_seeds)

diff = set(old) - set(new)

print len(diff)

with open(outfile, "w") as f_out:
	for d in diff:
		print d
		f_out.write(d+"\n")


