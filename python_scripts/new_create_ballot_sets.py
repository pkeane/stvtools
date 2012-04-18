from operator import itemgetter, attrgetter
from random import randint,shuffle
import copy
import math
import os
import stvtools
import sys
import time

def generate_ballot_set(cands,voters,output_file):
    fh = open(output_file,"w")
    ballots = []
    # for each voter
    for v in range(0,int(voters)):
        list = []
        # make list of candidates
        for c in range(1,int(cands)+1):
            list.append('c'+str(c))
        # shuffle
        shuffle(list)
        # append this ballot to set of ballots
        ballots.append(list) 
    # sort ballots by first place vote
    ballots = sorted(ballots, key=itemgetter(0))
    # from 0 to number_of_candidates (i.e. "places")
    # this is so we have each row being a "place"
    for place in range(0,int(cands)):
        set = []
        # this test *should* allow for non-full ballots
        # but we'll need to add an "else" clause
        for bal in ballots:
            if bal[place]:
                set.append(bal[place])
        # write out this "place"
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

def put_first(list,cellval):
  list.remove(cellval)
  newlist = [cellval]
  newlist.extend(list)
  return newlist

def put_first_and_second(list,pair):
    (c1,c2) = pair 
    list.remove(c1)
    list.remove(c2)
    newlist = [c1,c2]
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

def create_ties(data,seats,voters,ties):
    votes_per_tie = voters//ties
    cand_list= get_candidates(data)

    tied_cands = cand_list[0:ties]
    # make each ballot a ROW instead of a COL
    swapped_data = swap(data)
    # counter is simply the ballot number that a particular
    # cand tops.  It should go 0 to total_num_of_tied_ballots
    counter = 0
    for cand in tied_cands:
        for i in range(votes_per_tie):
            ballot = swapped_data[counter]
            swapped_data[counter] = put_first(ballot,cand)
            counter += 1

    num_remaining_ballots = len(swapped_data) - counter

    # now fix remaining
    # under what circumstances can we get too many ties?
    # when there are enough remaining ballots to (by chance)
    # include another set of (votes_per_tie) ties
    # OR if voters%ties >= votes_per_tie
    if voters-(votes_per_tie*ties) >= votes_per_tie:
        # remaining candidates
        remaining = cand_list[ties:]
        # cycle through remaining cands, putting each at the top of a remaining
        # ballot (votes_per_tie - 1) times until you run out of ballots
        for rc in remaining:
            for j in range(votes_per_tie-1):
                # make sure we have ballots left to fix
                if len(swapped_data) > counter:
                    ballot = swapped_data[counter]
                    # print("BALLOT INDEX "+str(counter)+" CAND "+rc)
                    swapped_data[counter] = put_first(ballot,rc)
                    counter += 1
    
    return swap(swapped_data)

def create_2deep_ties(data,seats,voters,ties):
    votes_per_tie = voters//ties
    cand_list= get_candidates(data)

    if len(cand_list) < 2*ties:
        print("CANNOT do second place ties.  Not enough candidates ("+str(ties)+" ties, "+str(len(cand_list))+" candidates, "+str(seats)+" seats)")
        return

    tied_cands1 = cand_list[0:ties]
    tied_cands2 = cand_list[ties:2*ties]
    cand_pairs = [(tied_cands1[i],tied_cands2[i]) for i in range(len(tied_cands1))]

    # make each ballot a ROW instead of a COL
    swapped_data = swap(data)
    # counter is simply the ballot number that a particular
    # cand tops.  It should go 0 to total_num_of_tied_ballots
    counter = 0
    for cand_pair in cand_pairs:
        for i in range(votes_per_tie):
            ballot = swapped_data[counter]
            swapped_data[counter] = put_first_and_second(ballot,cand_pair)
            counter += 1

    num_remaining_ballots = len(swapped_data) - counter

    # 2-DEEP coordination check
    # do we have enough candidates for 1st & 2nd place ties?
    # do we have enough candidates to spread out over remaining ballots?
    if len(cand_list)-2*ties < (num_remaining_ballots//votes_per_tie)*2:
        print("CANNOT do second place ties.  Not enough candidates ("+str(ties)+" ties, "+str(len(cand_list))+" candidates, "+str(seats)+" seats)")
        return
    else:
        pass

    # now fix remaining
    # for 2-deep we only need to worry about first place
    # in remainder ballots, because in first two rounds, we will
    # never see the second place in these remainder ballots
    # but we MUST make sure none of the tied second-place cands
    # appear as first in these remainder ballots

    # remaining candidates
    remaining = cand_list[2*ties:]
    # cycle through remaining cands, putting each at the top of a remaining
    # ballot (votes_per_tie - 1) times until you run out of ballots
    for rc in remaining:
        for j in range(votes_per_tie-1):
            # make sure we have ballots left to fix
            if len(swapped_data) > counter:
                ballot = swapped_data[counter]
                # debug technique
                # raw_input("BALLOT INDEX "+str(counter)+" CAND "+rc+" j is "+str(j)+" LEN Swapped is "+str(len(swapped_data)))
                swapped_data[counter] = put_first(ballot,rc)
                counter += 1
    
    return swap(swapped_data)

def file2tiedfile(output,voters,cands,seats,ties):
    csv_data = file2table(output)
    tied_data = create_ties(csv_data,seats,voters,ties)
    fh = open(output,"w")
    for row in tied_data:
        line = ','.join(row)
        fh.write(line+"\n") 
    # print("printed "+output)

def file2tiedfile2deep(output,voters,cands,seats,ties):
    csv_data = file2table(output)
    tied_data = create_2deep_ties(csv_data,seats,voters,ties)
    if not tied_data:
        # delete file
        os.remove(output)
        return
    fh = open(output,"w")
    for row in tied_data:
        line = ','.join(row)
        fh.write(line+"\n") 
    # print("printed "+output)

if __name__ == '__main__':

    VOTERS = 50
    SEATS = [6,7,8,9,10,11,12,13,14,15]
    CANDS = [20,25,30,35,40,45]
    NUM_PROFILES = 100
    # NUM_PROFILES = 1

    print('creating ballot sets')
    print('fixed number of voters is 50')
    print('fixed number of seats is 6/7/8/9/10/11/12/13/14/15')
    print('fixed number of candidates is 20/25/30/35/40/45')

    OUTDIR = 'ballots'
    start_time = time.time()
    processed_files = 0
    file_count = 103700 
    print(str(file_count)+' TOTAL files to process')

    for n in range(1,NUM_PROFILES+1):
        if not os.path.exists(OUTDIR):
            os.makedirs(OUTDIR)
        for c in CANDS:
            for s in SEATS:
                # the range of possible ties
                for t in range(2,s):
                    # test for Droop on ties sets
                    value_of_tied_ballots = (VOTERS//t)*100 
                    droop = (100*VOTERS//(s+1))+1
                    if value_of_tied_ballots < droop:
                        print("value of tied ballots: "+str(value_of_tied_ballots)+" is less than droop: "+str(droop))
                        print("Seats: "+str(s)+" Ties: "+str(t))
                    else:
                        # make 1 deep ballots
                        subdir = OUTDIR+'/c'+str(c)+'.s'+str(s)+'.t'+str(t)+'.d1'
                        if not os.path.exists(subdir):
                            os.makedirs(subdir)
                        output = OUTDIR+'/c'+str(c)+'.s'+str(s)+'.t'+str(t)+'.d1/c'+str(c)+'_s'+str(s)+'_t'+str(t)+'_d1-'+str(n)+'.txt'
                        generate_ballot_set(c,VOTERS,output)
                        file2tiedfile(output,VOTERS,c,s,t)
        
                        # make 2 deep ballots
#                        subdir = OUTDIR+'/c'+str(c)+'.s'+str(s)+'.t'+str(t)+'.d2'
#                        if not os.path.exists(subdir):
#                            os.makedirs(subdir)
#                        output = OUTDIR+'/c'+str(c)+'.s'+str(s)+'.t'+str(t)+'.d2/c'+str(c)+'_s'+str(s)+'_t'+str(t)+'_d2-'+str(n)+'.txt'
#                        generate_ballot_set(c,VOTERS,output)
#                        file2tiedfile2deep(output,VOTERS,c,s,t)
        
                    now = time.time()
                    elapsed_time = now - start_time
                    processed_files += 1
                    remaining_files = file_count - processed_files
                    avg_time_per_file = elapsed_time/processed_files
                    remaining_time = avg_time_per_file * remaining_files
                    min_left = remaining_time/60
                    print(str(remaining_files)+' files left')
                    print(str(min_left)+' minutes processing time left')
