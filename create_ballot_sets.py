from operator import itemgetter, attrgetter
from random import randint,shuffle
import copy
import math
import os
import stvtools
import sys

VOTERS = 50
SEATS = [6,7,8,9,10,11,12,13,14,15]
CANDS = [20,25,30,35,40,45]

def generate_ballot_set(cands,voters,output_file):
    fh = open(output_file,"w")
    ballots = []
    #for each voter
    for v in range(0,int(voters)):
        list = []
        #make list of candidates
        for c in range(1,int(cands)+1):
            list.append('c'+str(c))
        #shuffle
        shuffle(list)
        #append this ballot to set of ballots
        ballots.append(list) 
    #sort ballots by first place vote
    ballots = sorted(ballots, key=itemgetter(0))
    #from 0 to number_of_candidates (i.e. "places")
    # this is so we have each row being a "place"
    for place in range(0,int(cands)):
        set = []
        # this test *should* allow for non-full ballots
        # but we'll need to add an "else" clause
        for bal in ballots:
            if bal[place]:
                set.append(bal[place])
        #write out this "place"
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
    
def check_ties(data,ties,filename):
    cand_counts = {}
    out = ''
    for cand in data[0]:
        if cand not in cand_counts:
            cand_counts[cand] = 0
        cand_counts[cand] += 1
    counts = {}
    for c in cand_counts:
        if cand_counts[c] not in counts:
            counts[cand_counts[c]] = 0
        counts[cand_counts[c]] += 1
    sorted_ties = sorted(counts.items(), key=itemgetter(1))
    top = sorted_ties.pop()
    if top[1] != ties:
        print('PROBLEM!! '+str(top[1])+' TIES IN '+filename)

def put_first(list,cellval):
  list.remove(cellval)
  newlist = [cellval]
  newlist.extend(list)
  return newlist

def get_candidates(data):
  cands = {}
  for row in data:
    for cell in row:
      cands[cell] = 1
  cand_list = list(cands.keys())
  cand_list.sort()
  return cand_list

def create_ties(data,seats,ties):
  votes_per_tie = len(data[0])//ties
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

def file2tiedfile(filename,outdir,voters,cands,seats,ties):
    csv_data = file2table(filename)
    tied_data = create_ties(csv_data,seats,ties)
    tied_filename = outdir+'/c'+str(cands)+'_s'+str(seats)+'_t'+str(ties)+'.csv'
    fh = open(tied_filename,"w")
    for row in tied_data:
        line = ','.join(row)
        fh.write(line+"\n") 
    print("printed "+tied_filename)
    return tied_filename

if __name__ == '__main__':
    print('creating ballot sets')
    print('fixed number of voters is 50')
    print('fixed number of seats is 6/7/8/9/10/11/12/13/14/15')
    print('fixed number of candidates is 20/25/30/35/40/45')

    OUTDIR = 'ballots'

    for c in CANDS:
        output = OUTDIR+'/v50_c'+str(c)+'.csv'
        generate_ballot_set(c,VOTERS,output)
        print("created file "+output)
        for s in SEATS:
            for t in range(2,s):
                filename = file2tiedfile(output,OUTDIR,VOTERS,c,s,t)
                check_ties(file2table(filename),t,filename)
