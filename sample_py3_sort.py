from operator import itemgetter, attrgetter

dict = {}
dict['e'] = 2
dict['a'] = 7
dict['d'] = 9
dict['f'] = 1
dict['b'] = 4
dict['g'] = 2
dict['c'] = 6

sorted_x = sorted(dict.items(), key=itemgetter(1))
tup = sorted_x.pop()
