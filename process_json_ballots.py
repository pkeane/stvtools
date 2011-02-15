import simplejson as json
import os

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

def swap(data):
    table = []
    for i in range(len(data[0])):
        table.append([row[i] for row in data])
    return table

        


if __name__ == "__main__":
    BASEDIR = 'elections'
    for file in os.listdir(BASEDIR):
        fh = open(BASEDIR+'/'+file)
        data = json.loads(fh.read())
        print data['ELECTION']['id']
        # print fix_names(data['BALLOTS'])
        print swap(even_ballot_lengths(data['BALLOTS']))
