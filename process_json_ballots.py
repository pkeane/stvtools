import copy
import simplejson as json
import os
import sys

def fix_names(data):
    i = 0
    new_name = {}
    for c in get_cands(data):
        i += 1
        new_name[c] = 'c'+str(i)
    table = []
    for row in data:
        new_row = []
        for cell in row:
            new_row.append(new_name[cell])
        table.append(new_row)
    return table

def get_cands(data):
    cands = []
    for row in data:
        for cell in row:
            cands.append(cell)
    return sorted(list(set(cands)))

def even_ballot_lengths(ballotrows):
    ballot_length = len(get_cands(ballotrows))
    for ballot in ballotrows:
        diff = ballot_length - len(ballot)
        ballot.extend(['-' for i in range(diff)])
    return ballotrows

def check_ballots(data):
    for row in data:
        check_row = {}
        for cell in row:
            if cell not in check_row:
                check_row[cell] = 0
            check_row[cell] += 1
            if check_row[cell] > 1:
                print "PROBLEM: "+cell

def tweak(ballotrows,x,y):
    # note x & y are 1 based !!
    # and MUST be >= 1
    print x,y
    ballot = ballotrows[y-1]
    if len(ballot) > x and ballot[x-1] != '-' and ballot[x] != '-':
        first = ballot[x-1]
        second = ballot[x]
        ballotrows[y-1][x] = first 
        ballotrows[y-1][x-1] = second 
    return ballotrows

def diff(ballotrows1,ballotrows2):
    differences = '' 
    for i in range(len(ballotrows1)):
        for j in range(len(ballotrows1[i])):
            if ballotrows1[i][j] != ballotrows2[i][j]:
                differences += 'ballot {0} place {1} is different'.format(i,j)+"\n"
    return differences



def swap(data):
    table = []
    for i in range(len(data[0])):
        table.append([row[i] for row in data])
    return table

if __name__ == "__main__":
    TARGET = 'tweaked'
    BASEDIR = 'elections'
    for file in os.listdir(BASEDIR):
        fh = open(BASEDIR+'/'+file)
        data = json.loads(fh.read())
        year = data['ELECTION']['id']
        OUTDIR = TARGET+'/'+year
        if not os.path.exists(OUTDIR):
            os.makedirs(OUTDIR)
        # print fix_names(data['BALLOTS'])
        # print file
        # print check_ballots(data['BALLOTS'])
        ballotrows = even_ballot_lengths(fix_names(data['BALLOTS']))
        filename = "{0}-x0-y0.json".format(year)
        with open(OUTDIR+'/'+filename, mode='w') as f:
            json.dump(ballotrows, f)  
        num_y = len(ballotrows)
        num_x = len(ballotrows[0])
        for y in range(num_y):
            for x in range(num_x):
                tweaked = tweak(copy.deepcopy(ballotrows),x+1,y+1)
                # print diff(ballotrows,tweaked)
                filename = "{0}-x{1}-y{2}.json".format(year,x+1,y+1)
                with open(OUTDIR+'/'+filename, mode='w') as f:
                    json.dump(tweaked, f)  
                    print "printed {0}".format(filename)
