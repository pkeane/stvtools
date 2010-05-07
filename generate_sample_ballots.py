import random
import re
import simplejson as json

YEAR = 2000
SEATS = 10
VOTERS = 60

def dirify(str):
    str = re.sub('\&\;|\&', ' and ', str) 
    str = re.sub('[-\s]+', '_', str)
    return re.sub('[^\w\s-]', '', str).strip().lower()

data = {}
data['ELECTION'] = {}
data['ELECTION']['id'] = YEAR
data['ELECTION']['seats'] = SEATS
data['CANDIDATES'] = []
data['BALLOTS'] = []

f = open('sample_names')

for line in f:
    if '#' != line[0]:
        cand = {}
        cand['Name'] = line.strip()
        cand['EID'] = dirify(cand['Name'])
        if (random.randint(0,1)):
            cand['Full'] = 'Yes'
        else:
            cand['Full'] = 'No'
        if cand['Name']:
            data['CANDIDATES'].append(cand)

EID_SET = []

for cand in data['CANDIDATES']:
    EID_SET.append(cand['EID'])

for num in range(VOTERS):
    random.shuffle(EID_SET)
    ballot = []
    length_of_ballot = random.randint(1,len(data['CANDIDATES']))
    for num in range(length_of_ballot):
       ballot.append(EID_SET[num]) 
    data['BALLOTS'].append(ballot)

print json.dumps(data,sort_keys=True,indent=4)






