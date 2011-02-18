from operator import itemgetter, attrgetter
from random import randint,shuffle
import copy
import math
import os
import stvtools
import sys
import time

def swap(data):
    """
    swaps rows and columns always returns table 
    """
    table = []
    for i in range(len(data[0])):
        table.append([row[i] for row in data])
    return table

def get_candidates(data):
  cands = {}
  for row in data:
    for cell in row:
      cands[cell] = 1
  cand_list = list(cands.keys())
  cand_list.sort()
  return cand_list

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

def table2csv(data,out):
    print "printing "+out
    fh = open(out,"w")
    for row in data:
        line = ','.join(row)
        fh.write(line+"\n") 

if __name__=="__main__":
    BASEDIR = 'c30.s12.t6.d2'
    for file in os.listdir(BASEDIR):
        data = file2table(BASEDIR+'/'+file)
        print
        print file
        print
        cands = get_candidates(data)
        # set = [cands]
        matrix = []
        i = 0
        for ballot in swap(data):
            i += 1
            bal = ['ballot '+str(i)]
            for cand in cands:
                bal.append(str(1+ballot.index(cand)))
            matrix.append(bal)
        
        cands.reverse()
        cands.append('-')
        cands.reverse()

        matrix.reverse()
        matrix.append(cands)
        matrix.reverse()

        table2csv(swap(matrix),'matrix.csv')
        sys.exit()
