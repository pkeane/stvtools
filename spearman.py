import itertools
import os

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
    total = 0
    for n in list:
        total += n
    return n/len(list)

if __name__ == '__main__':
    BASEDIR = 'ballots'
    for file in os.listdir(BASEDIR):
        data = file2ballots(BASEDIR+'/'+file)
        rhos = []
        for pair in (list(itertools.combinations(list(range(len(data))),2))):
            rhos.append(get_rho(data[pair[0]],data[pair[1]]))
        print (file, '{0:f}'.format(get_avg(rhos)))

