import sys
from subprocess import Popen, PIPE, STDOUT

class Chunk(list):

    def __init__(self, chunk_type="", *args):
        list.__init__(self, *args)
        self.chunk_type = chunk_type

    def __str__(self):
        ls_str = " ".join("_".join(e) for e in self)
        return "[{:s} {:s} ]".format(self.chunk_type, ls_str)

    def __repr__(self):
        ls_str = "[{:s}]".format(", ".join(str(e) for e in self))
        return "Chunk(\"{:s}\", {})".format(self.chunk_type, ls_str)

    @property
    def head(self):
        return self.tokens[-1]

    @property
    def tokens(self):
        return zip(*self)[0]

    @classmethod
    def chunked_str_to_list(cls, chunked_str):
        chunked_str = chunked_str.strip().rstrip().split()
        chunks_list = []
        i = 0
        while i < len(chunked_str):
            part = chunked_str[i]
            if part.startswith("[N"):
                new_chunk = []
                chunk_type = part[1:]
                i += 1
                while not chunked_str[i].endswith("]"):
                    new_chunk.append(tuple((chunked_str[i].split("_"))))
                    i += 1

                possible_token = chunked_str[i][:-1]
                if possible_token != "":
                    new_chunk.append(tuple((possible_token.split("_"))))

                c = Chunk(chunk_type, new_chunk)
                chunks_list.append(c)
            elif part.startswith("[") or part.startswith("]"):
                pass
            else:
                tag_and_token = tuple(chunked_str[i].split("_"))
                if len(tag_and_token) != 2: # just in case
                    print tag_and_token
                    sys.exit()
                chunks_list.append(tag_and_token)

            i += 1

        return chunks_list

class OpenNLPChunkerWrapper:
    """	(Slightly incomplete) wrapper class for the opennlp command line
		interface.
	"""

    def __init__(self, install_loc, bin_loc):
        """Create a new wrapper object"""
        self.inst = install_loc
        self.bin = bin_loc
        self._start()


    def _start(self):
        """Initialize the parser with a specified model"""
        self.p = Popen([self.inst, 'ChunkerME', self.bin], stdout=PIPE, \
                       stdin=PIPE, stderr=STDOUT)
        temp = self.p.stdout.readline()
        self._flush()  #JUST IN CASE


    def _stop(self):
        """Close the subprocess!"""
        self.p = None


    def _flush(self):
        """Flush them buffers"""
        self.p.stdin.flush()
        self.p.stdout.flush()


    def chunk_sent(self, pos_tagged_sentence):
        """Parse a provided sentence"""
        pos_strings = map("_".join, pos_tagged_sentence)
        chunk_string = " ".join(pos_str for pos_str in pos_strings)
        chunk_string = chunk_string.encode("utf-8")
        if not self.p:
            self._start()
        self.p.stdin.write("%s\n" % chunk_string)
        res = self.p.stdout.readline()
        if res.strip().startswith("Invalid"):  #this happens when a parse is impossible
            res = self.p.stdout.readline()  #chunked output is better than nothing, no?
        self._flush()
        if res:
            return Chunk.chunked_str_to_list(res)
        else:
            return []

if __name__ == "__main__":
    chunker = OpenNLPChunkerWrapper("/home/keelan/lib/apache-opennlp-1.5.3/bin/opennlp", \
                                             "/home/keelan/lib/en-chunker.bin")
    c = chunker.chunk_sent([("Rockwell", "NNP"), ("said", "VBD"),
                           ("the", "DT"), ("agreement", "NN"), (".", ".")])
    print c
    print c[2]
    print c[0].head
