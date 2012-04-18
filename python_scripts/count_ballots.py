from operator import itemgetter
import os
import sys

def pretty_print_dict(dict):
    # sorted(list(ballot_tally.items()),key=itemgetter(1),reverse=True)
    for comb in dict:
        print('-----------------')
        print(comb)
        print(dict[comb]['count'])
        print(set(dict[comb]['seats']))
        print(set(dict[comb]['deep']))

if __name__ == "__main__":
    num = 0
    BASEDIR = 'ballots'

    count_per_cand_num = {}

    for subdir in os.listdir(BASEDIR):
        p = {}
        params = subdir.split('.')
        p['votes'] = 50
        p['cands'] = int(params[0].lstrip('c'))
        p['seats'] = int(params[1].lstrip('s'))
        p['ties'] = int(params[2].lstrip('t'))
        p['deep'] = int(params[3].lstrip('d'))

        for filename in os.listdir(BASEDIR+'/'+subdir):
            if 'c'+str(p['cands'])+'t'+str(p['ties']) not in count_per_cand_num:
                count_per_cand_num['c'+str(p['cands'])+'t'+str(p['ties'])] = {} 
                count_per_cand_num['c'+str(p['cands'])+'t'+str(p['ties'])]['count'] = 0
                count_per_cand_num['c'+str(p['cands'])+'t'+str(p['ties'])]['seats'] = []
                count_per_cand_num['c'+str(p['cands'])+'t'+str(p['ties'])]['deep'] = []
            count_per_cand_num['c'+str(p['cands'])+'t'+str(p['ties'])]['count'] += 1
            count_per_cand_num['c'+str(p['cands'])+'t'+str(p['ties'])]['seats'].append(p['seats'])
            count_per_cand_num['c'+str(p['cands'])+'t'+str(p['ties'])]['deep'].append(p['deep'])

            num += 1

    print num
    pretty_print_dict(count_per_cand_num)


