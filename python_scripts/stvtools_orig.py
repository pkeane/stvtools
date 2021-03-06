from operator import itemgetter, attrgetter
from random import randint,shuffle
import copy
import math
import optparse
import os
import sys
import time

"""
functions for running an STV election

data definitions:

    ballot -- a dictionary with two elements:
        'value': float indicating current value of the ballot
        'data': ordered list of candidate eids
    ballots -- an array of ballots

    candidate -- an object with five attributes:
            'eid': string
            'name': string
            'is_full_professor': Boolean
            'step_points': array of points at each step
            'points': points at current step
    candidates -- a dictionary of eid, candidate

    committee -- an array of candidates who have been elected
    ballot_tally -- a dictionary of eid, points of first position candidates
    logs -- an array of step logs

configuration variables:
    seats -- integer indicating the size of the committee to be elected
    minimum_full_professors
    initial_ballot_value
"""

class StvCandidate:
    def __init__(self, eid, name, is_full_professor, step_points, points):
        self.eid = eid
        self.name = name
        self.is_full_professor = is_full_professor
        self.step_points = step_points
        self.points = points 
    def __repr__(self):
        #return repr((self.eid,self.name,self.is_full_professor,self.step_points,self.points))
        return repr((self.name,self.eid,self.points))

def calculate_droop(num_of_ballots,seats,initial_ballot_value):
    """ compute Droop Quota 
    n.b. do not re-calculate droop after steps have begun
    Droop is determined by the original num of ballots.
    """
    droop = (initial_ballot_value*num_of_ballots//(seats+1))+1 # // means trunc
    return droop

def even_ballot_length(ballots):
    """ makes all ballots have the same length by appending
    array elements of '-' to each
    """
    max_length = max(len(ballot['data']) for ballot in ballots)
    for ballot in ballots:
        length = len(ballot['data'])
        ballot['data'].extend(['-'] * (max_length - length))
    return ballots

def ballots_to_table(ballots):
    """accepts an array of ballots and creates a table suitable for HTML 
    display. puts each ballot's value next to the first-place entry
    """
    #ballots = even_ballot_length(ballots)
    table = []
    #create rows
    for i in range(len(ballots[0]['data'])):
        row = [] 
        #create cells in row
        for ballot in ballots:
            if not i:
                #append value to top position (i.e., i == 0)
                row.append(ballot['data'][i]+'('+str(ballot['value'])+')')
            else:
                row.append(ballot['data'][i])
        table.append(row)
    return table

def tally_csv(data,seats):
    CONFIG = {}
    CONFIG['seats'] = seats 
    CONFIG['minimum_full_professors'] = 0 
    CONFIG['initial_ballot_value'] = 100 
    ballots = [] 
    for py_ballot in data['BALLOTS']: 
        b = {}
        b['data'] = py_ballot 
        b['value'] = CONFIG['initial_ballot_value']
        ballots.append(b)
    ballots = even_ballot_length(ballots)
    candidates = {} 
    for cand in data['CANDIDATES']: 
        full = True
        c = StvCandidate( cand, cand,full,[],0)
        candidates[cand] = c
    droop = calculate_droop(len(ballots),CONFIG['seats'],CONFIG['initial_ballot_value'])
    logs = [] 
    committee = []
    (ballots,candidates,committee,logs) = run_step(ballots,candidates,committee,CONFIG,droop,logs)
    return logs

def run_csv_tally(csv_file,seats,runs):
  """ This is a convenience function that runs multiple tallies over a 
  csv data set.  The csv should have lines of equal length.  Ballots
  are columns, rows are "places" (first row is first place on each
  ballot). Empty cells are OK, but columns are assumed to be continuous.
  cell values represent EID and Name (no distinction).  
  """
  csv_data = file2table(csv_file)
  cands = get_candidates(csv_data) 
  data = {}
  data['BALLOTS'] = swap(csv_data) 
  data['CANDIDATES'] = cands 
  was_elected = {}
  for i in range(runs):
      result = tally_csv(copy.deepcopy(data),seats)
      last = result.pop()
      for cand in last['committee']:
          if cand.eid in was_elected:
              was_elected[cand.eid] += 1
          else:
              was_elected[cand.eid] = 1
  sorted_elected = sorted(list(was_elected.items()),key=itemgetter(1),reverse=True)
  out = ''
  for tup in sorted_elected:
      out += tup[0]+' ('+ str(tup[1])+')\n'
  return out

def run_step(ballots,candidates,committee,config,droop,logs,step_count=0):
    """ This is the "master" function.  It can be called once, and will recurse
    until committee is full, outputting resulting data
    """
    seats = config['seats']
    log = {}
    log['step_count'] = step_count+1
    log['ballot_table'] = ballots_to_table(ballots)
    ballot_tally = get_ballot_tally(ballots) 
    no_votes = []
    for eid in candidates:
        if eid not in ballot_tally:
            no_votes.append(eid)

    no_votes.sort()
    log['no_votes'] = no_votes 
    log['ballot_tally'] = sorted(list(ballot_tally.items()),key=itemgetter(1),reverse=True)
    log['droop'] = droop
    log['tie_breaks'] = [] 
    # exit condition
    if len(committee) == seats: 
        return (ballots,candidates,committee,logs)
    else:
        candidates = set_candidate_points(candidates,ballot_tally)
        (candidates,ballots,committee,log) = elect_or_eliminate_one(candidates,ballots,committee,config,droop,log)
        # http://www.wellho.net/resources/ex.php4?item=y104/f2
        log['committee'] = committee[:] 
        logs.append(log)
        # recursion
        return run_step(ballots,candidates,committee,config,droop,logs,log['step_count'])

def get_ballot_tally(ballots):
    """ tally the points for each eid in ballot's first position """
    tally = {}
    for ballot in ballots:
        eid = ballot['data'][0]
        if '-' != eid:
            if eid not in tally:
                tally[eid] = 0
            tally[eid] += ballot['value']
    return tally

def set_candidate_points(candidates,ballot_tally):
    for eid in candidates:
        if eid in ballot_tally:
            candidates[eid].points = ballot_tally[eid]
            candidates[eid].step_points.append(ballot_tally[eid])
        else:
            candidates[eid].points = 0 
            candidates[eid].step_points.append(0)
    return candidates

def check_full_professor_constraint(candidates,ballots,committee,config,log):
    """ run this check AFTER a new committe member is added """
    purges = []
    max_non_full = config['seats'] - config['minimum_full_professors']
    (count_full,count_non_full) = get_committee_counts(committee)
    if max_non_full == count_non_full:
        #purge ballots of non-full
        for non in get_non_full_professors(candidates):
            ballots = purge_ballots_of_eid(ballots,non)
        #purge candidates of non-full
        for non in get_non_full_professors(candidates):
            purges.append(candidates[non].name)
            del candidates[non]
    log['full_professor'] = ', '.join(purges)
    return (candidates,ballots,log)

def get_non_full_professors(candidates):
    non_full = []
    for eid in candidates:
        if not candidates[eid].is_full_professor:
            non_full.append(eid)
    return non_full


def elect_or_eliminate_one(candidates,ballots,committee,config,droop,log):
    """ determine ONE candidate to elect or eliminate
    """
    seats = config['seats']
    if len(candidates):
        (winner,log) = get_winner(candidates,log)
        if winner.points >= droop:
            (ballots,log) = allocate_surplus(ballots,winner,droop,log)
            committee.append(winner)
            surplus = winner.points - droop
            log['report'] = "added "+winner.name+" ("+winner.eid+") to committee and distributed surplus of " + str(surplus)
            del candidates[winner.eid]
        else:
            #nobody has at least droop
            (loser,log) = get_loser(candidates,ballots,log)
            log['report'] = "removed "+loser.name+' ('+loser.eid+") from ballot"
            del candidates[loser.eid]
            ballots = purge_ballots_of_eid(ballots,loser.eid)
    (committee,log) = autofill_committee(candidates,ballots,committee,config,log)
    (candidates, ballots,log) = check_full_professor_constraint(candidates,ballots,committee,config,log)
    return (candidates,ballots,committee,log)

def autofill_committee(candidates,ballots,committee,config,log):
    """ fills remaining seats automatically when number
    of candidates left standing equals the number of open
    seats
    """
    additions = []
    seats = config['seats']
    if seats - len(committee) == len(get_ballot_tally(ballots)):
        for eid in get_ballot_tally(ballots):
            committee.append(candidates[eid])
            additions.append(candidates[eid].name);
    log['autofill'] = ', '.join(additions)
    return (committee,log)

def get_winner(candidates,log):
    candidates_sorted_by_points = sorted(list(candidates.values()),
                                         key=attrgetter('points'), reverse=True)
    if len(candidates) > 1 and candidates_sorted_by_points[0].points == candidates_sorted_by_points[1].points:
        #we have a tie
        tied_candidates = []
        highest_score = candidates_sorted_by_points[0].points
        for cand in candidates_sorted_by_points:
            if highest_score == cand.points:
                tied_candidates.append(cand)
        (winner,log) = break_most_points_tie(tied_candidates,candidates,log,0)
    else:
        #clear winner
        winner = candidates_sorted_by_points[0]
    return (winner,log) 

def get_loser(candidates,ballots,log):
    candidates_sorted_by_points = sorted(list(candidates.values()),
                                         key=attrgetter('points'))
    if len(candidates) > 1 and candidates_sorted_by_points[0].points == candidates_sorted_by_points[1].points:
        #we have a tie
        tied_candidates = []
        lowest_score = candidates_sorted_by_points[0].points
        for cand in candidates_sorted_by_points:
            if lowest_score == cand.points:
                tied_candidates.append(cand)
        (loser,log) = break_lowest_points_tie(tied_candidates,candidates,ballots,log,0)
    else:
        #clear loser 
        loser = candidates_sorted_by_points[0]
    return (loser,log)

def allocate_surplus(ballots,winner,droop,log):
    # equivalent to schwartz t - q
    surplus = winner.points - droop
    count = 0.0
    t_prime_value = 0.0
    # get count of x-ballots
    for ballot in ballots:
        # if winner is in first place on ballot AND
        # there is a 'next' candidate to give points to
        # count corresponds to schwartz p. 13 t'
        if winner.eid == ballot['data'][0] and '-' != ballot['data'][1]:
            count = count + 1
            t_prime_value += ballot['value']

    log['t_prime'] = t_prime_value
    log['winner_points'] = winner.points 

    beneficiaries = {}

    if t_prime_value and surplus:
        allocation = surplus/t_prime_value
    else:
        allocation = 0

    # allocate surplus
    for ballot in ballots:
        if winner.eid == ballot['data'][0] and '-' != ballot['data'][1]:
            ballot['value'] = ballot['value'] * allocation
            bene = ballot['data'][1]
            if bene in beneficiaries:
                beneficiaries[bene] += ballot['value'] 
            else:
                beneficiaries[bene] = ballot['value'] 

    log['beneficiaries'] = sorted(list(beneficiaries.items()),key=itemgetter(1),reverse=True)
    log['allocation'] = allocation

    #remove winner from ballots
    for ballot in ballots:
        if winner.eid in ballot['data']:
            ballot['data'].remove(winner.eid)
            #keep ballots same length
            ballot['data'].append('-')
    return (ballots,log)

def purge_ballots_of_eid(ballots,eid):
    for ballot in ballots:
        if eid in ballot['data']:
            ballot['data'].remove(eid)
            ballot['data'].append('-')
    return ballots

def break_most_points_tie(tied_candidates,all_candidates,log,run_count):
    """ returns ONE candidate; 'run_count' is incremented w/ each pass
    """
    if run_count:
        log['tie_breaks'].append(' tie between: '+', '.join(c.eid for c in tied_candidates)+' at step '+str(run_count))
    else:
        log['tie_breaks'].append(' tie between: '+', '.join(c.eid for c in tied_candidates))


    # per schwartz p. 7, we only need to check historical
    # steps through step k (current) - 1 (e.g., first round go
    # straight random. run_count is zero indexed, so we add 1
    if log['step_count'] == run_count+1:
        r = randint(0,len(tied_candidates)-1)
        log['tie_breaks'].append('*** coin toss ***')
        return (tied_candidates[r],log)

    historical_step_points = {}
    # create eid->points dictionary for [run_count] historical step
    for c in tied_candidates:
        historical_step_points[c.eid] = c.step_points[run_count]
    #sorted tuples are (eid,score) pairs
    sorted_tuples = sorted(list(historical_step_points.items()), key=itemgetter(1), reverse=True)
    if sorted_tuples[0][1] > sorted_tuples[1][1]:
        # clear winner
        return (all_candidates[sorted_tuples[0][0]],log)
    else:
        #we have a tie
        new_tied_candidates = []
        highest_score = sorted_tuples[0][1]
        for cand_tup in sorted_tuples:
            if highest_score == cand_tup[1]:
                #append as candidate object
                new_tied_candidates.append(all_candidates[cand_tup[0]])
        # recursion
        return break_most_points_tie(new_tied_candidates,all_candidates,log,run_count+1)

def second_preference_low_tiebreak(tied_candidates,all_candidates,ballots,log,depth=1):
    if depth == len(ballots[0]['data']):
        r = randint(0,len(tied_candidates)-1)
        log['tie_breaks'].append('**** coin toss ****')
        return (tied_candidates[r],log)
    else:
        log['tie_breaks'].append('** considering points at preference number '+str(depth+1))
        log['tie_breaks'].append(' tie between: '+', '.join(c.eid for c in tied_candidates))

    tallies = {}

    for ballot in ballots:
        for cand in tied_candidates:
            if cand.eid == ballot['data'][depth]:
                if cand.eid in tallies:
                    tallies[cand.eid] += 1
                else:
                    tallies[cand.eid] = 1

    if 0 == len(tallies):
        #recursion
        return second_preference_low_tiebreak(tied_candidates,all_candidates,ballots,log,depth+1)

    new_tied_candidates = []

    if 1 == len(tallies):
        #remove this person from list of tied
        for cand in tied_candidates:
            if list(tallies.keys()).pop() != cand.eid:
                new_tied_candidates.append(cand)
        if 1 == len(new_tied_candidates):
            return (new_tied_candidates[0],log)
        else:
            return second_preference_low_tiebreak(new_tied_candidates,all_candidates,ballots,log,depth+1)

    #create array of tuples (eid,tally) sorted by tally
    sorted_tuples = sorted(list(tallies.items()), key=itemgetter(1))
    if sorted_tuples[0][1] < sorted_tuples[1][1]:
        # clear loser 
        return (all_candidates[sorted_tuples[0][0]],log)
    else:
        common_low_score = sorted_tuples[0][1]
        for eid in tallies:
            if tallies[eid] == common_low_score:
                new_tied_candidates.append(all_candidates[eid])
        #recursion
        return second_preference_low_tiebreak(new_tied_candidates,all_candidates,ballots,log,depth+1)

def break_lowest_points_tie(tied_candidates,all_candidates,ballots,log,run_count):
    """ returns ONE candidate; 'run_count' is incremented w/ each pass
    """
    if run_count:
        log['tie_breaks'].append(' tie between: '+', '.join(c.eid for c in tied_candidates)+' at step '+str(run_count))
    else:
        log['tie_breaks'].append(' tie between: '+', '.join(c.eid for c in tied_candidates))

    # per schwartz p. 7, we only need to check historical
    # steps through step k (current) - 1 (e.g., first round go
    # straight random. run_count is zero indexed, so we add 1
    if log['step_count'] == run_count+1:
        # for lowest, if points = 0, no further processing is necessary
        if  0 == tied_candidates[0].points:
            r = randint(0,len(tied_candidates)-1)
            log['tie_breaks'].append('*** coin toss ***')
            return (tied_candidates[r],log)
        else:
            """
            "...we examine the ballots (at step k) on which the surviving
            tied candidates are ranked first and select those tied candidates
            with the lowest second-preference vote total in this subset of
            ballots, then those among the latter candidates with the lowest
            third-preference total, etc.  Only then do we break any remaining
            tie randomly."
            """
            considered_ballots = []
            tied_eids = []
            for cand in tied_candidates:
                tied_eids.append(cand.eid)
            for ballot in ballots:
                if ballot['data'][0] in tied_eids:
                    considered_ballots.append(ballot)
            return second_preference_low_tiebreak(tied_candidates,all_candidates,considered_ballots,log)

    historical_step_points = {}
    # create eid->points dictionary for [run_count] historical step
    for c in tied_candidates:
        historical_step_points[c.eid] = c.step_points[run_count]
    #sorted tuples are (eid,score) pairs
    sorted_tuples = sorted(list(historical_step_points.items()), key=itemgetter(1))
    if sorted_tuples[0][1] < sorted_tuples[1][1]:
        # clear lowest 
        return (all_candidates[sorted_tuples[0][0]],log)
    else:
        #we have a tie
        new_tied_candidates = []
        lowest_score = sorted_tuples[0][1]
        for cand in sorted_tuples:
            if lowest_score == cand[1]:
                #append as candidate object
                new_tied_candidates.append(all_candidates[cand[0]])
        # recursion
        return break_lowest_points_tie(new_tied_candidates,all_candidates,ballots,log,run_count+1)

def get_committee_counts(committee):
    full = 0
    non_full = 0
    for candidate in committee:
        if candidate.is_full_professor:
            full = full + 1
        else:
            non_full = non_full + 1
    return (full,non_full) 

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
    
def get_candidates(data):
  cands = {}
  for row in data:
    for cell in row:
      cands[cell] = 1
  cand_list = list(cands.keys())
  cand_list.sort()
  return cand_list

if __name__ == '__main__':
    start = time.time()
    seats = 7
    ties = 2
    runs = 300
    votes = 50
    file = 'test.csv'
    csv_data = file2table(file)
    cands = len(get_candidates(csv_data))
    droop = calculate_droop(votes,seats,100)
    print('reading file "'+file+'"')
    print(str(cands)+" candidates")
    print(str(seats)+" seats")
    print("droop is "+str(droop))
    print("\nresults:")
    print(run_csv_tally(file,seats,runs))
    now = time.time()
    dur = now-start
    print('took '+str(dur)+'secs')

if __name__ == '__xmain__':
    BASEDIR = 'ballots'
    file_count = 0
    for root, dirs, files in os.walk(BASEDIR):
        for name in files:
            file_count += 1
    print(str(file_count)+' TOTAL files to process')
    start_time = time.time()
    processed_files = 0
    # BASEDIR = 'test'
    outfile = 'instability_'+str(int(start_time))
    fh = open(outfile,"w")
    BASEDIR = 'ballots'
    for subdir in os.listdir(BASEDIR):
        params = subdir.split('.')
        votes = 50
        runs = 1000
        # runs = 10
        cands = int(params[0].lstrip('c'))
        seats = int(params[1].lstrip('s'))
        ties = int(params[2].lstrip('t'))
        deep = int(params[3].lstrip('d'))

        for file in os.listdir(BASEDIR+'/'+subdir):
            filepath = BASEDIR+'/'+subdir+'/'+file
            csv_data = file2table(filepath)
            cands = len(get_candidates(csv_data))
            droop = calculate_droop(votes,seats,100)

            print('reading file "'+file+'"')
            print(str(cands)+" candidates")
            print(str(seats)+" seats")
            print("droop is "+str(droop))

            print("\nresults:")
            print(run_csv_tally(filepath,seats,runs))

            now = time.time()
            elapsed_time = now - start_time
            processed_files += 1
            remaining_files = file_count - processed_files
            avg_time_per_file = elapsed_time/processed_files
            remaining_time = avg_time_per_file * remaining_files
            left = remaining_time/3600
            print(str(left)+' hours processing time left (approx)')
