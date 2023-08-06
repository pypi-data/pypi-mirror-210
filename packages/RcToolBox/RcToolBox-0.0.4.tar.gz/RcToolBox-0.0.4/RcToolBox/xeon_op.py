#!/usr/bin/env python
# from multiprocessing import Pool
from pathos.multiprocessing import ProcessingPool as Pool
from RcToolBox.basic_op import sprint

""" 
Here we use pathos.multiprocessing. Unlike python's multiprocessing module, 
pathos.multiprocessing can directly utilize functions that require multiple arguments
"""

def hardcore_process(function, *args, num_workers=4):
    
    res = None
    sprint("We will use {} cpu threads!".format(num_workers))
    # *with ... as ... is a context manager, which will automatically close the pool
    with Pool(num_workers) as p:
        res = p.map(function, *args)

    
    if res is None:
        print("Return of multiprocessing is None, please check your input and function!")
    return res

def add(a, b):
    return a + b

if __name__ == '__main__':
    
    x = [1, 2, 3, 4, 5]
    y= [2, 2, 3, 4, 5]
    res = hardcore_process(add, x, y,num_workers=4)
    print(res)