from operator import itemgetter, attrgetter
from random import randint,shuffle
import copy
import itertools
import math
import optparse
import os
import sys
import time


if __name__ == '__main__':
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
    this_dur = 0
    shortest_dur = 20 
    longest_dur = 1
    shortest_file = ''
    longest_file = ''
    last_end_time = start_time 
    for subdir in os.listdir(BASEDIR):
        params = subdir.split('.')
        votes = 50
        runs = 1000
        # runs = 10
        cands = int(params[0].lstrip('c'))
        if int(partition) != cands:
            continue
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
            print(run_csv_tally(filepath,seats,runs,droop))
            print("measure of coordination: ")
            print(get_mc(filepath))

            now = time.time()
            this_dur = now - last_end_time
            last_end_time = now
            if this_dur < shortest_dur:
                shortest_dur = this_dur
                shortest_file = file
            if this_dur > longest_dur:
                longest_dur = this_dur
                longest_file = file

            print("this iteration: "+str(this_dur)+" seconds")
            print("shortest iteration: "+str(shortest_dur)+" seconds ("+shortest_file+")")
            print("longest iteration: "+str(longest_dur)+" seconds ("+longest_file+")")

            elapsed_time = now - start_time
            processed_files += 1
            remaining_files = file_count - processed_files
            avg_time_per_file = elapsed_time/processed_files
            print("average iteration: "+str(avg_time_per_file)+" seconds")
            print("")
            remaining_time = avg_time_per_file * remaining_files
            left = remaining_time/3600
            print(str(left)+' hours processing time left (approx)')
