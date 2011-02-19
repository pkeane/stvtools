#from multiprocessing import Process, Pool
import multiprocessing as mp 
import os
import time

def info(title):
    print title
    print 'module name:', __name__
    print 'parent process:', os.getppid()
    print 'process id:', os.getpid()

def f(name):
    info('function f')
    print 'hello', name

def fx(x):
    time.sleep(.3)
    return x*x 

if __name__ == '__xmain__':
    info('main line')
    p = mp.Process(target=f, args=('bob',))
    p.start()
    p.join()


if __name__ == '__main__':
    print mp.cpu_count()
    pool = mp.Pool(processes=10)              # start 4 worker processes
    result = pool.apply_async(fx, [10])     # evaluate "f(10)" asynchronously
    print result.get(timeout=1)           # prints "100" unless your
    print pool.map(fx, range(100))  
