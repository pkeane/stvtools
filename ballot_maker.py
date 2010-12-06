from operator import itemgetter, attrgetter
from random import randint,shuffle
import copy
import math
import optparse
import sys

def generate_ballot_set(cands,voters,output_file):
    fh = open(output_file,"w")
    ballots = []
    for v in range(0,int(voters)):
        list = []
        for c in range(1,int(cands)+1):
            list.append('c'+str(c))
        shuffle(list)
        ballots.append(list) 
    ballots = sorted(ballots, key=itemgetter(0))
    for place in range(0,int(cands)):
        set = []
        for bal in ballots:
            if bal[place]:
                set.append(bal[place])
        line = ','.join(set)
        fh.write(line+"\n") 

if __name__ == '__main__':
    p = optparse.OptionParser()
    p.add_option('--candidates','-c', default=10)
    p.add_option('--voters','-v', default=30)
    p.add_option('--output','-o', dest="output", default="out.csv")
    data, args = p.parse_args()

    generate_ballot_set(data.candidates,data.voters,data.output)
    print "created file "+data.output
