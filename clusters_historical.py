try:
    import json
except:
    import simplejson as json
from operator import itemgetter, attrgetter
from random import randint,shuffle
import copy
import math
import os
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

def get_name_from_eid(eid):
    pass

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

def json_file2table(filename):
    fh = open(filename)
    return json.loads(fh.read())

def table2csv(data,out):
    fh = open(out,"w")
    for row in data:
        line = ','.join(row)
        fh.write(line+"\n") 

def get_subsets(list):
   list = [x for x in list if x != '-']
    # from http://wiki.python.org/moin/Powerful%20Python%20One-Liners 
   return [[y for j, y in enumerate(set(list)) if (i >> j) & 1] for i in range(2**len(set(list)))]

if __name__=="__main__":
    BASEDIR = 'c30.s12.t6.d2'
    seats = 12
    for file in os.listdir(BASEDIR):
        data = file2table(BASEDIR+'/'+file)
        data = json_file2table('2010-no_swap.json')
        ties = {}
        for b in data:
            if b[0] not in ties:
                ties[b[0]] = 0
            ties[b[0]] += 1
        # print ties 
        #print
        #print file
        #print
        cands = get_candidates(data)
        clusters = {} 
        for ballot in swap(data):
            #print 
            #print "BALLOT ",ballot
            #print
            for i in range(12):
                sub = tuple(sorted(ballot[0:i+1]))
                #int 
                # print "WORKING ON ",sub
                #print 
                if sub not in clusters:
                    clusters[sub] = 0
                clusters[sub] += 1
                # print "\tadd 1 to ",sub

                subsets = get_subsets(sub)

                for ss in subsets:
                    if len(ss) > 0:
                        tss = tuple(sorted(ss))
                        if tss not in clusters:
                            clusters[tss] = 0
                        # print "\tadd "+str(len(ss))+'/'+str(len(sub))+ " to ",tss
                        clusters[tss] += float(len(ss))/len(sub)
        
        tally = sorted(list(clusters.items()),key=itemgetter(1),reverse=True)
        for t in tally:
            if t[1] > 1:
                print ", ".join(t[0])+" ("+str(t[1])+")"
##            print
##            print "FINAL cluster tallies for this ballot: "
##            print
##            tally = sorted(list(clusters.items()),key=itemgetter(1),reverse=True)
##            for t in tally:
##                if t[1] > 1:
##                    print str(t[0])+" scores "+str(t[1])
##            sys.exit()
        sys.exit()
