from tkFileDialog import askopenfilename      
try:
    import json
except:
    import simplejson as json
from Tkinter import * 
import copy
import time
import tkFont 
from operator import itemgetter, attrgetter
from random import randint

VERSION = "STV Tools v.1.0"

ABOUT_TEXT = """
about text and licensing here.
"""
HELP_TEXT = """
STV Tools Help text here
"""

def rfc3339():
    """ Format a date the way Atom likes it (RFC3339)
    """
    return time.strftime('%Y-%m-%dT%H:%M:%S%z')

class ScrolledText(Frame):
    """ from O'Reilly Programming Python 3rd ed.
    """
    def __init__(self, parent=None, text='', file=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)                 # make me expandable
        self.makewidgets()
        self.settext(text, file)
    def makewidgets(self):
        sbar = Scrollbar(self)
        text = Text(self, relief=SUNKEN,height=18)
        sbar.config(command=text.yview)                  # xlink sbar and text
        text.config(yscrollcommand=sbar.set)             # move one moves other
        sbar.pack(side=RIGHT, fill=Y)                    # pack first=clip last
        text.pack(side=LEFT, expand=YES, fill=BOTH)      # text clipped first
        self.text = text
    def addtext(self,text):
        self.text.insert(END,text+"\n")
        self.text.focus()                                # save user a click
    def settext(self, text='', file=None):
        if file: 
            text = open(file, 'r').read()
        self.text.delete('1.0', END)                     # delete current text
        self.text.insert('1.0', text)                    # add at line 1, col 0
#        self.text.mark_set(INSERT, '1.0')                # set insert cursor
        self.text.focus()                                # save user a click
    def gettext(self):                                   # returns a string
        return self.text.get('1.0', END+'-1c')           # first through last

class AutoScrollbar(Scrollbar):
    # a scrollbar that hides itself if it's not needed.  only
    # works if you use the grid geometry manager.
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            # grid_remove is currently missing from Tkinter!
            self.tk.call("grid", "remove", self)
        else:
            self.grid()
        Scrollbar.set(self, lo, hi)
    def pack(self, **kw):
        raise TclError, "cannot use pack with this widget"
    def place(self, **kw):
        raise TclError, "cannot use place with this widget"

class Application():
    def __init__(self, master):

        frame = Frame(master)
        frame.pack(fill=BOTH,padx=2,pady=2)

        self.f1 = tkFont.Font(family="arial", size = "14", weight = "bold")
        self.titleLabel = Label(frame, width=38, padx = '3', pady = '3', font = self.f1, text = (VERSION),anchor=W)
        self.titleLabel.pack()

        self.report = ScrolledText(frame)

        menu = Menu(frame)
        root.config(menu=menu)

        filemenu = Menu(menu)
        menu.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Open...", command=self.get_data_file)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=root.quit)

        self.run_button = Button(frame, text="Run Tally with 1 iteration",command=self.run_tally)
        self.run_button.pack(side=LEFT)

        self.clear_button = Button(frame, text="Clear",command=self.clear)
        self.clear_button.pack(side=RIGHT)



        self.iterations = 1

        filemenu = Menu(menu)
        menu.add_cascade(label="Iterations", menu=filemenu)
        filemenu.add_command(label="1", command=lambda: self.set_iterations(1))
        filemenu.add_command(label="10", command=lambda: self.set_iterations(10))
        filemenu.add_command(label="100", command=lambda: self.set_iterations(100))
        filemenu.add_command(label="1000", command=lambda: self.set_iterations(1000))
        filemenu.add_command(label="5000", command=lambda: self.set_iterations(5000))

        self.write("use the \"File\" menu to open a data file")

        self.frame = frame

    def write(self,text,delete_text=False):
        if delete_text:
            self.report.settext(text)
        else:
            self.report.addtext(text)

    def clear(self):
        self.report.settext('')

    def set_iterations(self,num):
        self.iterations = num 
        if self.run_button:
            self.run_button.pack_forget()
        self.run_button = Button(self.frame, text="Run Tally with "+str(num)+" iterations",command=self.run_tally)
        self.run_button.pack(side=LEFT)

    def run_tally(self):
        self.write('-- NEW TALLY SET '+rfc3339()+' ('+self.election['id']+' / '+self.election['seats']+' Seats) --\n\n',True)
        new_data = {} 
        for col in self.matrix:
            ballot = []
            for row in self.matrix[col]:
                ballot.append(self.matrix[col][row].get())
            new_data[col] = ballot

        self.write('-- data edits --')

        for i in range(len(self.ballots)):
            for j in range(len(new_data[i])):
                if new_data[i][j] != self.ballots[i][j]:
                    self.write("on ballot "+str(i+1)+" place "+str(j+1)+" was \""+self.ballots[i][j]+"\" and is now \""+new_data[i][j]+"\"")

        self.write('\n-- running '+str(self.iterations)+' iterations --');

        was_elected = {}
        for i in range(self.iterations):
            result = self.do_tally(new_data)
            last = result.pop()
            for cand in last['committee']:
                if cand.eid in was_elected:
                    was_elected[cand.eid] += 1
                else:
                    was_elected[cand.eid] = 1

        sorted_elected = sorted(was_elected.items(),key=itemgetter(1),reverse=True)
        for tup in sorted_elected:
            self.write(tup[0]+' ('+ str(tup[1])+')')

    def do_tally(self,ballot_data):
        ballot_data = copy.deepcopy(ballot_data)
        CONFIG = {}
        CONFIG['seats'] = int(self.election['seats']) 
        CONFIG['minimum_full_professors'] = 4 
        CONFIG['initial_ballot_value'] = 100 
    
        ballots = [] 
        for i in ballot_data: 
            b = {}
            b['data'] = ballot_data[i] 
            b['value'] = CONFIG['initial_ballot_value']
            ballots.append(b)

        candidates = {} 
        for py_cand in self.candidates: 
            if 'Yes' == py_cand['Full']: 
                full = True
            else:
                full = False
            c = StvCandidate( py_cand['EID'], py_cand['Name'],full,[],0)
            candidates[py_cand['EID']] = c
    
        droop = calculate_droop(len(ballots),CONFIG['seats'],CONFIG['initial_ballot_value'])
        logs = [] 
        committee = []
        (ballots,candidates,committee,logs) = run_step(ballots,candidates,committee,CONFIG,droop,logs)
        return logs


    def even_ballot_length(self):
        """ makes all ballots have the same length by appending
        array elements of '-' to each
        """
        ballots = self.ballots
        max_length = max(len(ballot) for ballot in ballots)
        for ballot in ballots:
            length = len(ballot)
            ballot.extend(['-'] * (max_length - length))
        return ballots
    
    def get_data_file(self):
        filename = askopenfilename(filetypes=[("JSON data", ".json"),("All files", "*")])
        fn = open(filename)
        json_data = fn.read()
        data = json.loads(json_data)
        self.ballots = data['BALLOTS']
        self.election = data['ELECTION']
        self.candidates = data['CANDIDATES']
        ballots = self.even_ballot_length()
        max_length = max(len(ballot) for ballot in ballots)

        top = Toplevel(root)
        top.geometry('+25+400')

        vscrollbar = AutoScrollbar(top)
        vscrollbar.grid(row=0, column=1, sticky=N+S)
        hscrollbar = AutoScrollbar(top, orient=HORIZONTAL)
        hscrollbar.grid(row=1, column=0, sticky=E+W)
        
        canvas = Canvas(top,
                        yscrollcommand=vscrollbar.set,
                        xscrollcommand=hscrollbar.set,
                        height=300,width=600)
        canvas.grid(row=0, column=0, sticky=N+S+E+W)
        
        vscrollbar.config(command=canvas.yview)
        hscrollbar.config(command=canvas.xview)
        
        # make the canvas expandable
        top.grid_rowconfigure(0, weight=1)
        top.grid_columnconfigure(0, weight=1)
        
        #
        # create canvas contents
        
        frame = Frame(canvas)
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(1, weight=1)

        dict = {}
        self.matrix = {} 
        for row in range(max_length):
            for col in range(len(ballots)):
                if row == 0:
                    self.matrix[col] = {}
                    label1 = Label(frame, width=8, text='ballot '+str(col+1))
                    label1.grid(row=row, column=col,padx =0,pady=0) 
                entry1 = Entry(frame, width=9,bd=1)
                entry1.insert(0,ballots[col][row])
                entry1.grid(row=row+1,column=col,pady=0,padx=0)
                self.matrix[col][row] = entry1

        canvas.create_window(0, 0, anchor=NW, window=frame)
        frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
        #self.write('selected file '+filename)
        self.write('Election ID: '+self.election['id'])
        self.write('Number of Seats: '+self.election['seats'])
        #self.write(' *** edit data in grid, then run tally')

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
    #compute
    raw_droop = initial_ballot_value*num_of_ballots/(seats+1)
    #round up to nearest integer
    return int(round(raw_droop +.5))

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
    log['ballot_tally'] = sorted(ballot_tally.items(),key=itemgetter(1),reverse=True)
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
    candidates_sorted_by_points = sorted(candidates.values(),
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
    candidates_sorted_by_points = sorted(candidates.values(),
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

    log['beneficiaries'] = sorted(beneficiaries.items(),key=itemgetter(1),reverse=True)
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
    sorted_tuples = sorted(historical_step_points.items(), key=itemgetter(1), reverse=True)
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
            if tallies.keys().pop() != cand.eid:
                new_tied_candidates.append(cand)
        if 1 == len(new_tied_candidates):
            return (new_tied_candidates[0],log)
        else:
            return second_preference_low_tiebreak(new_tied_candidates,all_candidates,ballots,log,depth+1)

    #create array of tuples (eid,tally) sorted by tally
    sorted_tuples = sorted(tallies.items(), key=itemgetter(1))
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
    sorted_tuples = sorted(historical_step_points.items(), key=itemgetter(1))
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

if __name__ == "__main__":
    root = Tk()
    root.title(VERSION)
    root.geometry('+25+25')
    app = Application(root)
    root.mainloop() 
