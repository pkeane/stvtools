import simplejson as json
import os

def fix_names(data):
    cands = []
    for row in data:
        for cell in row:
            cands.append(cell)
    i = 0
    new_name = {}
    for c in sorted(list(set(cands))):
        i += 1
        new_name[c] = 'c'+str(i)
    table = []
    for row in data:
        new_row = []
        for cell in row:
            new_row.append(new_name[cell])
        table.append(new_row)
    return table


        


if __name__ == "__main__":
    BASEDIR = 'elections'
    for file in os.listdir(BASEDIR):
        fh = open(BASEDIR+'/'+file)
        data = json.loads(fh.read())
        print data['ELECTION']['id']
        print fix_names(data['BALLOTS'])
