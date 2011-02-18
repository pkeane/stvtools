try:
    import json
except:
    import simplejson as json
from operator import itemgetter, attrgetter
from random import randint

def rfc3339():
    """ Format a date the way Atom likes it (RFC3339)
    """
    return time.strftime('%Y-%m-%dT%H:%M:%S%z')


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
        self.clear()
        self.write('processing file...')
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


if __name__ == "__main__":
  print "ss"
