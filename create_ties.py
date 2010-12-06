from operator import itemgetter, attrgetter
from random import randint,shuffle
import copy
import math
import optparse
import os
import sys

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
    cands = {}
    out = ''
    for cand in data[0]:
        if not cands.has_key(cand):
            cands[cand] = 0
        cands[cand] += 1
    for c in cands:
      if cands[c] > 1:
        out += c+" has "+str(cands[c])+" first place votes\n"
    return out

def put_first(list,cellval):
  list.remove(cellval)
  newlist = [cellval]
  newlist.extend(list)
  return newlist

def get_possible_ties(data,seats):
  votes = len(data[0])
  droop = (votes/(seats+1))+1
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
  droop = (len(data[0])/(seats+1))+1
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
    p.add_option('--seats','-s', default=10)
    p.add_option('--ties','-t', default=3)
    p.add_option('--input','-i', dest="input", default="out.csv")
    p.add_option('--output','-o', dest="output")
    data, args = p.parse_args()
    if not os.path.exists(data.input):
      print "please indicate a CSV input file: -i <myfile.csv>"
      sys.exit()

    csv_data = file2table(data.input)
    cands = len(get_candidates(csv_data))
    voters = len(csv_data[0])
    droop = (voters/(int(data.seats)+1))+1

    print "using file "+str(data.input)+" as input"

    poss = get_possible_ties(csv_data,int(data.seats))
    if int(data.ties) not in poss:
      print "Sorry, invalid number of ties ("+str(data.ties)+") given that the number of seats is "+str(data.seats) 
      print "number must be between "+str(poss[0])+' and '+str(poss.pop())
      sys.exit()
    else:
      ties = int(data.ties)
      seats = int(data.seats)
      tied_data = create_ties(csv_data,seats,ties)
      if data.output:
        filename = data.output
      else:
        filename = 'v'+str(voters)+'_c'+str(cands)+'_s'+str(data.seats)+'_t'+str(data.ties)+'.csv'
      fh = open(filename,"w")
      for row in tied_data:
        line = ','.join(row)
        fh.write(line+"\n") 
      print "created file "+filename
