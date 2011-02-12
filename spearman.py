import itertools
import os
import time

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

def get_coordination_measure_no_ties(filename):
    filedata = file2table(filename)
    rhos = []
    # make each ballot a row (instead of a column)
    data = swap(filedata)
    for pair in (list(itertools.combinations(list(range(len(data))),2))):
        rhos.append(get_rho(data[pair[0]],data[pair[1]]))
    return get_avg(rhos)

def get_coordination_measure(filename):
    filedata = file2table(filename)
    toppers = filedata[0]
    factions = {}
    for i in range(len(toppers)):
        if toppers[i] not in factions:
            factions[toppers[i]] = []
        factions[toppers[i]].append(i)
    votes_per_tie = max([len(x) for x in factions.values()])
    # get only factions that are in fact a set of tied ballots
    sets = [fac for fac in factions.values() if len(fac) == votes_per_tie]
    # print("FACTIONS: ", sets)
    rhos = []
    # create a faction data set
    # make each ballot a row (instead of a column)
    swapped_data = swap(filedata)
    for set in sets:
        data = []
        for j in set:
            data.append(swapped_data[j])
        # data is now a faction of votes 
        # get rhos w/in this faction
        for pair in (list(itertools.combinations(list(range(len(data))),2))):
            rhos.append(get_rho(data[pair[0]],data[pair[1]]))
    return get_avg(rhos)
    #print(file,'{0:f}'.format(get_avg(rhos)))

def get_rho(list1,list2):
    cands = sorted(list(set(list1+list2)))
    sum_ofDsquared = 0
    for cand in cands:
        rank1 = list1.index(cand)
        rank2 = list2.index(cand)
        # print (rank1,rank2)
        D = (rank1-rank2)
        Dsquared = D**2
        sum_ofDsquared += Dsquared
    
    # print(sum_ofDsquared)
    c = len(cands)
    return 1-(float(6*sum_ofDsquared)/(c*(c**2-1)))

def file2ballots(filename):
    """
    converts a ballot_set file to a list of ballots (each a list)
    """
    return swap(file2table(filename))

def get_avg(list):
    return sum(list)/len(list)

if __name__ == '__main__':
    BASEDIR = 'ballots'
    file_count = 0
    for root, dirs, files in os.walk(BASEDIR):
        for name in files:
            file_count += 1
    print(str(file_count)+' TOTAL files to process')
    exit()
    start_time = time.time()
    processed_files = 0
    # BASEDIR = 'test'
    outfile = 'coordination_measures_'+str(int(start_time))
    fh = open(outfile,"w")
    BASEDIR = 'ballots'
    for subdir in os.listdir(BASEDIR):
        for file in os.listdir(BASEDIR+'/'+subdir):
            params = subdir.split('.')
            ties = int(params[2].lstrip('t'))

            if ties:
                cm = get_coordination_measure(BASEDIR+'/'+subdir+'/'+file)
            else:
                cm = get_coordination_measure_no_ties(BASEDIR+'/'+subdir+'/'+file)

            line = file+' {0:f}'.format(cm)
            fh.write(line+"\n") 
    
            now = time.time()
            elapsed_time = now - start_time
            processed_files += 1
            remaining_files = file_count - processed_files
            avg_time_per_file = elapsed_time/processed_files
            remaining_time = avg_time_per_file * remaining_files
            min_left = remaining_time/60
            print(str(min_left)+' minutes processing time left (approx)')


