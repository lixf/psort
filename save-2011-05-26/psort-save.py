import random
import hsv
from Tkinter import *
from collections import deque

# Create a random permutation of values 0 through n-1
def randperm(n):
    if n == 0:
        return []
    ls = randperm(n-1)
    ls.append(n-1)
    idx = random.randint(0,n-1)
    t1 = ls[idx]
    t2 = ls[n-1]
    ls[idx] = t2
    ls[n-1] = t1
    return ls

# Possible permutation orders are:
# forward: low to high
# reverse: high to low
# random: Random permutation
# highlowhigh: From high to low and back to high
# lowhighlow: From low to high and back to low
orders = ['forward', 'reverse', 'random', 'lowhighlow', 'highlowhigh']

def genperm(n, order='forward'):
    if order == 'forward':
        return range(0,n)
    if order == 'reverse':
        return [n-1-x for x in range(0,n)]
    if order == 'random':
        return randperm(n)
    if order == 'lowhighlow':
        return [(2*x if x < (n+1)/2 else 2*(n-x)-1) for x in range(0,n)]
    if order == 'highlowhigh':
        return [(n-1-2*x if x < (n+1)/2 else 2*x-n) for x in range(0,n)]
    else:
        return range(0,n)        

# Get first element of tuple
def tfirst((a,b)):
    return a

# Invert permutation
def pinvert(p):
    n = len(p)
    pairs = [(p[i],i) for i in range(0,n)]
    npairs = sorted(pairs, key = tfirst)
    return [b for (a,b) in npairs]
    
# Compose permutations: i --> p(q(i))
def pcompose(p, q):
    return [p[q[i]] for i in range(0, len(p))]

# Some global state
count = 0
# perm indicates permutation of values
perm = []
# Keys controls effect of sorting.  Is also a permutation
keys = []
# Colors a fixed spectrum of colors
colors = []
# Display is TK window
display = []
displayactive = False
# Canvas is canvas within display
canvas = []
# Items is a list of drawing elements, arranged by position
items = []
# Height of rectangles
rheight = 200
# Width of rectangles
rwidth = 40
# Width of screen
swidth = 1440

# Time step.  Changes based on sorting method
cycle = 400
# Mapping from sort method to time step
cycles = {'evenodd':400,
          'selection':30,
          'insertion':30,
          'dinsertion':30,
          'random':30,
          'quick':100,
          'swap':50}

# Keep track of last ordering
lastorder = 'none'

# Sorting methods
methods = cycles.keys()

def initsort(n=40, order='random', width=0):
    global count, perm, keys, colors
    global display, canvas, displayactive
    global rheight, rwidth, swidth
    global lastorder
    count = n
    perm = genperm(count, order=order)
    keys = range(0,count)
    lastorder = order
    colors = hsv.spectrum(n)
    if (width > 0):
        swidth = width
    if displayactive:
        display.destroy()
        display.active = False
    if (count * rwidth > swidth):
        rwidth = int(swidth/count)
    display = Tk()
    displayactive = True
    display.title('Sorting %d elements' % count)
    canvas = Canvas(display,
                    width=rwidth*count, height=rheight, background="#ffffff")
    canvas.grid(row=0, column=0)
    showsort(perm)
#    display.mainloop()

def issorted(perm, keys):
    for i in range(0,len(perm)-1):
        if keys[perm[i]] > keys[perm[i+1]]:
            return False
    return True

# Swap two elements in permutation
def swap(perm, i, j, show=False):
    global colors, cycle
    global canvas
    global rheight, rwidth
    if i == j:
        return
    if i >= 0 and i < len(perm) and j >= 0 and j < len(perm):
        (v1, v2) = (perm[i], perm[j])
        (perm[i], perm[j]) = (v2, v1)
        if show and canvas:
            c1 = colors[perm[i]]
            c2 = colors[perm[j]]
            i1 = items[i]
            i2 = items[j]
            items[i] = canvas.create_rectangle(rwidth * i, 0,
                                               rwidth * (i+1), rheight,
                                               fill = '%s' % c1)
            items[j] = canvas.create_rectangle(rwidth * (j), 0,
                                               rwidth * (j+1), rheight,
                                               fill = '%s' % c2)
            canvas.delete(i1)
            canvas.delete(i2)
            canvas.update()
            canvas.after(cycle)

# Compare two adjacent elements and swap if needed
def testandswap(perm, keys, i, j, show=False):
    if (i >= 0 and i < len(perm)
        and j >= 0 and j < len(perm)
        and keys[perm[i]] > keys[perm[j]]):
        swap(perm, i, j, show)
        return True
    return False

def showsort(perm):
    global colors, cycle
    global canvas
    global rheight, rwidth
    global items
    if canvas:
        for item in items:
            canvas.delete(item)
        items = []
        for i in range(0,len(perm)):
            color = colors[perm[i]]
            item = canvas.create_rectangle(rwidth * i, 0,
                                           rwidth * (i+1), rheight,
                                           fill = '%s' % color)
            items.append(item)
        canvas.update()
        canvas.after(cycle)
    else:
        print perm
        
# Parallel sort by swapping adjacent elements
# Alternate between odd and even values of initial index to avoid races
def evenoddsort(perm, keys):
    parity = 0
    while not issorted(perm, keys):
        map (lambda idx: testandswap(perm, keys,
                                     parity + 2*idx, parity + 2*idx + 1),
             range(0, int(len(perm)/2)))
        parity = 1-parity
        showsort(perm)
             
# Selection sort
def selectionsort(perm, keys):
    parity = False
    while not issorted(perm, keys):
        for i in range(0, len(perm)-1):
            idx = i if parity else len(perm)-i-2
            testandswap(perm, keys, idx, idx+1, True)
        parity = not parity

# Insertion sort
def insertionsort(perm, keys):
    # Insert i+1 into list 0:i
    for i in range(0, len(perm)-1):
        for idx in [i-j for j in range(0,i+1)]:
            if not testandswap(perm, keys, idx, idx+1, True):
                break

# Double-ended Insertion sort
def doubleinsertionsort(perm, keys):
    # Invariant: elements [left:right] are sorted
    left = len(perm)/2
    right = left
    while left > 0 or right < len(perm)-1:
        # Insert i from left into [left:right] to get [left-1:right]
        for i in range(left-1, right-1):
            testandswap(perm, keys, i, i+1, True)
        # Insert i from right into [left-1:right] to get [left-1:right+1]
        for i in [left+right-2-j for j in range(left-2, right+1)]:
            testandswap(perm, keys, i, i+1, True)
        left = left - 1
        right = right + 1

# Random sort
def randomsort(perm, keys):
    while not issorted(perm, keys):
        for i in randperm(len(perm)-1):
            testandswap(perm, keys, i, i+1, True)

# Get two distinct numbers between 0 and n-1
def getpair(n):
    while True:
        i = random.randint(0, n-1)
        j = random.randint(0, n-1)
        if i < j:
            return (i,j)
        if j < i:
            return (j,i)

def swapsort(perm, keys):
    while not issorted(perm, keys):
        (i,j) = getpair(len(perm))
        testandswap(perm, keys, i, j, True)

# Functions for quicksort
def pivotidx(start, count):
    return start + count/2

def partition(perm, keys, start, count, pivot):
    left = start
    right = start + count - 1
    while (True):
        while left <= right and keys[perm[left]] <= pivot:
            left = left + 1
        while left <= right and pivot <= keys[perm[right]]:
            right = right - 1
        if (left < right):
            swap(perm, left, right, True)
            left = left + 1
            right = right - 1
        else:
            break
    return left

   
# Recursive quicksort
def rqsort(perm, keys, start=0, count=-1):
    if (count < 0):
        count = len(perm) - start
    p = pivotidx(start, count)
    pivot = keys[perm[p]]
    right = start + count - 1
    swap(perm, p, right, True)
    middle = partition(perm, keys, start, count-1, pivot)
    swap(perm, middle, right, True)
    if (middle > start):
        rqsort(perm, keys, start, middle - start)
    if (middle < right):
        rqsort(perm, keys, middle+1, right-middle)
    
# Quicksort using list to serve as stack or queue
# Seems like breadth-first is more interesting visually
def qsort(perm, keys, breadth=True):
    # Each element contains (start, count) pair
    todo = deque([(0, len(perm))])
    while len(todo) > 0:
        if breadth:
            (start, count) = todo.popleft()
        else:
            (start, count) = todo.popright()
        p = pivotidx(start, count)
        pivot = keys[perm[p]]
        right = start + count - 1
        swap(perm, p, right, True)
        middle = partition(perm, keys, start, count-1, pivot)
        swap(perm, middle, right, True)
        if (middle > start):
            ns = start
            nc = middle-start
            todo.append((ns,nc))
        if (middle < right):
            ns = middle+1
            nc = right-middle
            todo.append((ns,nc))

def runsort(method='random', order='forward', c = 10000):
    global cycle
    global perm, keys
    global lastorder
    keys = pinvert(genperm(len(perm), order=order))
    cycle = cycles[method]
    if c < 10000:
        cycle = c
    if method == 'evenodd':
        evenoddsort(perm, keys)
    elif method == 'selection':
        selectionsort(perm, keys)
    elif method == 'insertion':
        insertionsort(perm, keys)
    elif method == 'dinsertion':
        doubleinsertionsort(perm, keys)
    elif method == 'random':
        randomsort(perm, keys)
    elif method == 'quick':
        qsort(perm, keys)
    elif method == 'swap':
        swapsort(perm, keys)
    lastorder = order

# Get random element from list
def randele(ls):
    i = random.randint(0, len(ls)-1)
    return ls[i]

def run(s=100):
    global canvas, lastorder
    for i in range(0,s):
        method=randele(methods)
        while True:
            order=randele(orders)
            if order != lastorder:
                break
        print "Sorting with method %s to get %s order" % (method, order)
        runsort(method=method, order=order)
        canvas.after(1000)




    
