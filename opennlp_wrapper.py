from subprocess import Popen, PIPE, STDOUT

class Chunk(list):

    def __init__(self, chunk_type="", *args):
        list.__init__(self, *args)
        self.chunk_type = chunk_type
        self.tokens = zip(*self)[0]

    def __str__(self):
        return "Chunk(\"{:s}\", {})".format(self.chunk_type, repr(self))


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
        if not self.p:
            self._start()
        self.p.stdin.write("%s\n" % chunk_string)
        res = self.p.stdout.readline()
        if res.strip().startswith("Invalid"):  #this happens when a parse is impossible
            res = self.p.stdout.readline()  #chunked output is better than nothing, no?
        self._flush()
        if res:
            return self.chunked_str_to_list(res)
        else:
            return []

    def chunked_str_to_list(self, chunked_str):
        chunked_str = chunked_str.strip().rstrip().split()
        chunks_list = []
        i = 0
        while i < len(chunked_str):
            part = chunked_str[i]
            if part.startswith("["):
                new_chunk = []
                chunk_type = part[1:]
                i += 1
                while chunked_str[i] != "]":
                    new_chunk.append(tuple((chunked_str[i].split("_"))))
                    i += 1
                c = Chunk(chunk_type, new_chunk)
                chunks_list.append(c)
            else:
                tag_and_token = tuple(chunked_str[i].split("_"))
                assert len(tag_and_token) == 2 # just in case
                chunks_list.append(Chunk("", [tag_and_token]))

            i += 1

        return chunks_list

if __name__ == "__main__":
    chunker = OpenNLPChunkerWrapper("/home/keelan/lib/apache-opennlp-1.5.3/bin/opennlp", \
                                             "/home/keelan/lib/en-chunker.bin")
    chunker.chunk_sent([("Rockwell", "NNP"), ("said", "VBD"),
                           ("the", "DT"), ("agreement", "NN"), (".", ".")])