from operator import itemgetter, attrgetter
import pprint
import simplejson as json
import stvtools
import sys

pp = pprint.PrettyPrinter(indent=4)

def tally(json_data):
    try:
        data = json.loads(json_data)
    except:
        return "invalid file"
    election = data['ELECTION'] 
    CONFIG = {}
    CONFIG['seats'] = int(election['seats']) 
    CONFIG['minimum_full_professors'] = 4 
    CONFIG['initial_ballot_value'] = 100 

    ballots = [] 
    for py_ballot in data['BALLOTS']: 
        b = {}
        b['data'] = py_ballot 
        b['value'] = CONFIG['initial_ballot_value']
        ballots.append(b)

    ballots = stvtools.even_ballot_length(ballots)

    candidates = {} 
    for py_cand in data['CANDIDATES']: 
        if 'Yes' == py_cand['Full']: 
            full = True
        else:
            full = False
        c = stvtools.StvCandidate( py_cand['EID'], py_cand['Name'],full,[],0)
        candidates[py_cand['EID']] = c

    droop = stvtools.calculate_droop(len(ballots),CONFIG['seats'],CONFIG['initial_ballot_value'])
    logs = [] 
    committee = []
    (ballots,candidates,committee,logs) = stvtools.run_step(ballots,candidates,committee,CONFIG,droop,logs)
    return logs

if __name__=="__main__":
    data = open('2010.json').read()
    was_elected = {}
    for i in range(1000):
        result = tally(data)
        last = result.pop()
        for cand in last['committee']:
            if cand.eid in was_elected:
                was_elected[cand.eid] += 1
            else:
                was_elected[cand.eid] = 1
    

    sorted_elected = sorted(was_elected.items(),key=itemgetter(1),reverse=True)
    for tup in sorted_elected:
        print tup[0]+' ('+ str(tup[1])+')'

