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

def file2table(filename):
    fh = open(filename)
    table = []
    for ln in fh.readlines():
        row = []
        ln = ln.strip()
        for cell in ln.split(','):
            row.append(cell)
        table.append(row)
    return table

def swap(data):
    """
    swaps rows and columns always returns table 
    """
    table = []
    max_row_length = sorted([len(row) for row in data],reverse=True)[0]
    for i in range(max_row_length):
        table.append([])
    for row in data:
        for i in range(max_row_length):
            if i < len(row):
                table[i].append(row[i])
            else:
                table[i].append('')
    return table
    
def view_ties(data):
    """ for testing """
    first = data[0].strip('\n').split(',')
    cands = {}
    for cand in first:
        if not cands.has_key(cand):
            cands[cand] = 0
        cands[cand] += 1
    print cands

def put_first(list,cellval):
  list.remove(cellval)
  newlist = [cellval]
  newlist.extend(list)
  return newlist

def get_droop(data,seats):
  """ this assume each ballot value is 1 """
  return int(math.floor(float(len(data[0]))/(float(seats)+1))) + 1

def get_possible_ties(data,seats):
  votes = len(data[0])
  droop = get_droop(data,seats)
  most = seats-1
  if droop*most > votes:
    most = votes/droop 
  return range(2,most+1)

def get_candidates(data):
  cands = {}
  for row in data:
    for cell in row:
      cands[cell] = 1
  cand_list = cands.keys()
  cand_list.sort()
  return cand_list

def create_ties(data,seats,ties):
  if ties not in get_possible_ties(data,seats):
    raise Exception('creating '+str(ties)+' ties is not possible')
  droop = get_droop(data,seats)
  votes_per_tie = len(data[0])/ties
  cand_list= get_candidates(data)
  tied_cands = cand_list[0:ties]
  swapped_data = swap(data)
  counter = 0
  for cand in tied_cands:
    for i in range(votes_per_tie):
      ballot = swapped_data[counter]
      swapped_data[counter] = put_first(ballot,cand)
      counter += 1
  return swap(swapped_data)

if __name__ == '__main__':
    p = optparse.OptionParser()
    p.add_option('--candidates','-c', default=10)
    p.add_option('--voters','-v', default=30)
    p.add_option('--seats','-s', default=6)
    p.add_option('--ties','-t', default=0)
    p.add_option('--output','-o', dest="output", default="out.csv")
    p.add_option('--input','-i', dest="input", default="out.csv")
    data, args = p.parse_args()

    generate_ballot_set(data.candidates,data.voters,data.output)
    print "created file "+data.output

    if data.ties:
      csv_data = file2table(tally_file)
      poss = get_possible_ties(csv_data,int(data.seats))
      if int(data.ties) not in poss:
        print "Sorry, invalid number of ties ("+str(data.ties)+") given that the number of seats is "+str(data.seats) 
        print "number must be between "+str(poss[0])+' and '+str(poss.pop())
        sys.exit()
      else:
        ties = int(data.ties)
        seats = int(data.seats)
        tied_data = create_ties(csv_data,seats,ties)
        filename = 'out_'+str(data.seats)+'seats_'+str(data.ties)+'ties.csv'
        fh = open(filename,"w")
        for row in tied_data:
          line = ','.join(row)
          fh.write(line+"\n") 
        print "created file "+filename




