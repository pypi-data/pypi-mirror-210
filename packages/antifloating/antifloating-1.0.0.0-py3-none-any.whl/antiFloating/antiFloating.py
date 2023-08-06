import math

def define(number): # make float into list [integer, number that time 10 to make this integer]
    for i in range(0, 100):
        if(number == int(number)):
            break
        number *= 10
    num_list = [number, i]
    return num_list

def get(numlist):   # make list [integer, number that time 10 to make this integer] into float <- unused
    for i in range(numlist[1]):
        numlist[0] /= 10
    return (numlist[0])

def add(*args): # add float without floating point error
    list = args
    result = 0
    numlist = []
    floatlist = []
    
    for i in range(len(list)):
        numlist.append(define(list[i])[0])
        floatlist.append(define(list[i])[1])
        
    for i in range(len(floatlist)):
        for o in range(floatlist[i], max(floatlist)):
            numlist[i] *= 10
           
    for i in range(len(numlist)):
        result += numlist[i]
        
    result /= math.pow(10, max(floatlist))
        
    return result

def time(*args):    # time float without floating point error
    list = args
    result = 0
    numlist = []
    floatlist = []
    
    for i in range(len(list)):
        numlist.append(define(list[i])[0])
        floatlist.append(define(list[i])[1])
        
    for i in range(len(floatlist)):
        for o in range(floatlist[i], max(floatlist)):
            numlist[i] *= 10
            
    result = numlist[0]
           
    for i in range(1, len(numlist)):
        result *= numlist[i]
        
    result /= math.pow(10, sum(floatlist))
        
    return result

def sub(*args): # subtract float without floating point error <- useless
    list = args
    result = list[0]
    for i in range(1, len(list)):
        result -= list[i]
    return result

def div(*args): # add float without floating point error <- useless
    list = args
    result = list[0]
    for i in range(1, len(list)):
        result /= list[i]
    return result
        