try:
    import json
except:
    import simplejson as json
import copy
import os
import sys

def fix_names(data,name_lookup):
    i = 0
    new_name = {}
    for c in get_cands(data):
        i += 1
        new_name[c] = 'c'+str(i)
        # new_name[c] = name_lookup[c]
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

def tweak(ballotrows,nb,nr):
    # note x & y are 1 based !!
    # and MUST be >= 1
    ballot = ballotrows[nb-1]
    if len(ballot) > nr and ballot[nr-1] != '-' and ballot[nr] != '-':
        first = ballot[nr-1]
        second = ballot[nr]
        ballotrows[nb-1][nr] = first 
        ballotrows[nb-1][nr-1] = second 
    return ballotrows

def diff(ballotrows1,ballotrows2):
    differences = '' 
    for i in range(len(ballotrows1)):
        for j in range(len(ballotrows1[i])):
            cand_was = ballotrows1[i][j]
            cand_is = ballotrows2[i][j]
            if cand_was != cand_is:
                differences += 'ballot {0} rank {1} was {2} is now {3}'.format(i,j,cand_was,cand_is)+"\n"
    return differences

def swap(data):
    table = []
    for i in range(len(data[0])):
        table.append([row[i] for row in data])
    return table

if __name__ == "__main__":
    TARGET = 'historical'
    BASEDIR = 'elections'
    for file in os.listdir(BASEDIR):
        fh = open(BASEDIR+'/'+file)
        data = json.loads(fh.read())
        year = data['ELECTION']['id']
        name_lookup = {}
        import re
        for c in data['CANDIDATES']:
            name_lookup[c['EID']] = re.sub('[^a-zA-Z]','',c['Name'])
        if int(year) > 2001:
            OUTDIR = TARGET+'/'+year
            if not os.path.exists(OUTDIR):
                os.makedirs(OUTDIR)
            # print fix_names(data['BALLOTS'])
            # print file
            # print check_ballots(data['BALLOTS'])

            # print year, fix_names(data['BALLOTS'])
            ballotrows = even_ballot_lengths(fix_names(data['BALLOTS'],name_lookup))
            # filename = "{0}-x0-y0.json".format(year)
            filename = "{0}-no_swap.json".format(year)
            with open(OUTDIR+'/'+filename, mode='w') as f:
                json.dump(ballotrows, f)  
            num_ballots = len(ballotrows)
            num_ranked = len(ballotrows[0])
            for nb in range(num_ballots):
                for nr in range(num_ranked):
                    tweaked = tweak(copy.deepcopy(ballotrows),nb+1,nr+1)
                    differences = diff(ballotrows,tweaked)
                    if differences:
                        #print differences
                        # filename = "{0}-x{1}-y{2}.json".format(year,x+1,y+1)
                        filename = "{0}-ballot{1}-cand_at_rank{2}_swapped_with_cand_at_rank{3}.json".format(year,nb+1,nr+1,nr+2)
                        with open(OUTDIR+'/'+filename, mode='w') as f:
                            json.dump(tweaked, f)  
                            print "printed {0}".format(filename)
