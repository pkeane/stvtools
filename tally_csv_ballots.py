import csv
import json
import sys
import stvtools
from operator import itemgetter, attrgetter
from random import randint

"""
converts from cvs ballots as columns to ballots as json
"""
CONFIG = {}
CONFIG['initial_ballot_value'] = 100
CONFIG['minimum_full_professors'] = 0

def do_tally(ballot_data):
  row_ballots = {} 
  for place in ballot_data:
    if place[0] == 'seats':
      CONFIG['seats'] = int(place[1])
    elif place[0] == 'voters':
      CONFIG['voters'] = place[1]
    elif place[0] == 'candidates':
      CONFIG['candidates'] = place[1]
    else:
      voter = 0;
      for vote in place:
        voter += 1
        if not row_ballots.has_key("v"+str(voter)):
          row_ballots["v"+str(voter)] = []
        row_ballots["v"+str(voter)].append(vote)
  
  ballots = [] 
  for i in row_ballots: 
    b = {}
    b['data'] = row_ballots[i] 
    b['value'] = 100 
    ballots.append(b)
  
  candidates = {}
  for n in range(1,int(CONFIG['candidates'])+1):
    full = True
    eid = 'c'+str(n)
    c = stvtools.StvCandidate(eid,eid,full,[],0)
    candidates['c'+str(n)] = c
  
  droop = stvtools.calculate_droop(len(ballots),CONFIG['seats'],CONFIG['initial_ballot_value'])
  logs = [] 
  committee = []
  (ballots,candidates,committee,logs) = stvtools.run_step(ballots,candidates,committee,CONFIG,droop,logs)
  return logs


if __name__ == "__main__":
  if sys.argv[1]:
    filename = sys.argv[1]
  
  ballot_data = []
  for row in csv.reader(open(filename)):
    ballot_data.append(row)
  was_elected = {}
  for i in range(500):
    result = do_tally(ballot_data)
    last = result.pop()
    for cand in last['committee']:
      if cand.eid in was_elected:
        was_elected[cand.eid] += 1
      else:
        was_elected[cand.eid] = 1
  sorted_elected = sorted(was_elected.items(),key=itemgetter(1),reverse=True)
  for tup in sorted_elected:
    print(tup[0]+' ('+ str(tup[1])+')')
  
