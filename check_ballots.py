from operator import itemgetter, attrgetter
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

def check_ties(data,p):
    if 0 == p['deep']:
        print('OK NO ties '+p['filename'])
        return

    for depth in range(p['deep']):
        cand_counts = {}
        for cand in data[depth]:
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
        if top[1] != p['ties']:
            print('PROBLEM!! '+str(top[1])+' TIES IN '+filename)
        else:
            print('OK '+str(depth+1)+' ties '+p['filename'])

def check_data(data,p):
    """
    make sure all ballots are the same length and have all candidates once
    """
    for place in data:
        if len(place) != p['votes']:
            print("ERROR: num votes")
            sys.exit()

    for vote in swap(data):
        if len(vote) != len(set(vote)):
            print("ERROR: not a full unique set of candidates")
            sys.exit()
        if len(vote) != p['cands']:
            print(len(vote))
            print(p['cands'])
            print("ERROR: num cands")
            sys.exit()

    print('OK data '+p['filename'])



if __name__ == "__main__":
    BASEDIR = 'ballots'
    for subdir in os.listdir(BASEDIR):
        print(subdir)
        p = {}
        params = subdir.split('.')
        p['votes'] = 50
        p['cands'] = int(params[0].lstrip('c'))
        p['seats'] = int(params[1].lstrip('s'))
        p['ties'] = int(params[2].lstrip('t'))
        p['deep'] = int(params[3].lstrip('d'))

        for filename in os.listdir(BASEDIR+'/'+subdir):
            p['filename'] = filename
            data = file2table(BASEDIR+'/'+subdir+'/'+filename)
            check_data(data,p)
            check_ties(data,p)


