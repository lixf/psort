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

# Find set of pairs of form (i,i+1) with no overlaps
def randpairs(n):
    bits = [random.randint(0,1) for i in range(0,n)]
    lbits = bits[0:-1]
    rbits = bits[1:]
    choose = [1 if lbits[i] == 1 and rbits[i] == 0 else 0 for i in range(0,n-1)]
    return [(i,i+1) for i in range(0,n-1) if choose[i] == 1]

# Get random element from list
def randele(ls):
    i = random.randint(0, len(ls)-1)
    return ls[i]

# Get two distinct numbers between 0 and n-1
def getpair(n):
    while True:
        i = random.randint(0, n-1)
        j = random.randint(0, n-1)
        if i < j:
            return (i,j)
        if j < i:
            return (j,i)

# Possible permutation orders are:
# forward: low to high
# reverse: high to low
# random: Random permutation
# revfwd: From high to low and back to high
# fwdrev: From low to high and back to low
orders = ['forward', 'reverse', 'random', 'fwdrev', 'revfwd',
          'interleave'
# These orders did not prove very interesting
#          , 'fwdfwd', 'revrev']
]

def genperm(n, order='forward'):
    if order == 'forward':
        return range(0,n)
    if order == 'reverse':
        return [n-1-x for x in range(0,n)]
    if order == 'random':
        return randperm(n)
    if order == 'fwdrev':
        return [(2*x if x < (n+1)/2 else 2*(n-x)-1) for x in range(0,n)]
    if order == 'revfwd':
        return [(n-1-2*x if x < (n+1)/2 else 2*x-n) for x in range(0,n)]
    if order == 'fwdfwd':
        return [(2*x if x < (n+1)/2 else 2*(x-(n+1)/2)+1) for x in range(0,n)]
    if order == 'revrev':
        return [(n-1-2*x if x < (n+1)/2 else n-x-1) for x in range(0,n)]
    if order == 'interleave':
        return [(x/2 if x % 2 == 0 else n-(x+1)/2) for x in range(0,n)]
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

class Psort:
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
    # Difference between window height/width and image (determined empirically)
    windowdeltah = 4
    windowdeltaw = 4
    # Time step.  Changes based on sorting method
    cycle = 400
    # Multiplier times time step
    cyclemult = 1.0
    # Set to False to pause sorter
    running = True
    # Mapping from sort method to time step
    cycles = {'evenodd':400,
              'triple': 500,
              'merge': 350,
              'selection':30,
              'insertion':30,
              'dinsertion':30,
              'random':30,
              'quick':200,
              'swap':50}

    # Keep track of last ordering
    lastorder = 'none'
    # saturation and value for spectrum
    spectrum_s = 1.0
    spectrum_v = 1.0

    # What combinations of sorting method and target order
    # should be excluded for not being visually appealing
    taboopairs = set([('merge', 'random'),
                      ('selection', 'random'),
                      ('insertion', 'random'),
                      ('dinsertion', 'random'),
                      ('quick', 'random')])

    # Sorting methods
    methods = cycles.keys()

    def __init__(self, n=40, order='forward', width=0, height = 0,
                 saturation = 0, value = 0):
        self.count = n
        self.perm = genperm(n, order=order)
        self.keys = range(0, n)
        self.lastorder = order

        if saturation > 0:
            self.spectrum_s = saturation
        if value > 0:
            self.spectrum_v = value
        self.colors = hsv.spectrum(n, self.spectrum_s, self.spectrum_v)

        if width > 0:
            self.swidth = width
        if height > 0:
            self.rheight = height
        if self.displayactive:
            self.display.destroy()
        if (self.count * self.rwidth > self.swidth):
            self.rwidth = int(self.swidth/self.count)
        self.display = Tk()
        self.display.title('Sorting %d elements' % self.count)
        self.frame = Frame(self.display)
        self.frame.pack(fill=BOTH, expand=YES)
        self.canvas = Canvas(self.frame,
                             width=self.rwidth*self.count,
                             height=self.rheight,
                             background="#ffffff")
        self.canvas.pack(fill=BOTH, expand=YES)
        self.canvas.grid(row=0, column=0)
        self.displayactive = True
        self.showsort(firsttime=True)
        self.display.bind("<ButtonRelease-1>", self.showsort)

    # Update count for already running display
    def newcount(self, n=40):
        self.count = n
        if self.lastorder == 'none':
            self.lastorder = 'forward'
        self.perm = genperm(n, order=self.lastorder)
        self.keys = range(0, n)
        self.colors = hsv.spectrum(n, self.spectrum_s, self.spectrum_v)
        self.rwidth = int(self.swidth/self.count)
        if not self.displayactive:
            self.display = Tk()
            self.displayactive = True
            self.display.title('Sorting %d elements' % self.count)
            self.frame = Frame(self.display)
            self.frame.pack(fill=BOTH, expand=YES)
            self.canvas = Canvas(self.frame,
                                 width=self.rwidth*self.count,
                                 height=self.rheight,
                                 background="#ffffff")
            self.canvas.pack(fill=BOTH, expand=YES)
            self.canvas.grid(row=0, column=0)
            self.display.bind("<ButtonRelease-1>", self.showsort)
        else:
            self.display.title('Sorting %d elements' % self.count)
        self.showsort(firsttime=True)


    # Delay for t milliseconds if self.running is True
    # Start busy waiting if self.running = False
    def pause(self, t):
        while self.displayactive and not self.running:
            # Wait for 100 ms and check again
            self.canvas.after(100)
        if (self.displayactive and t > 0):
            self.canvas.after(t)

    def quit(self):
        if (self.displayactive):
            self.cyclemult = 0.0;
            self.display.destroy()
            self.displayactive = False

    def set_spectrum(self, s = -1, v = -1):
        if s >= 0:
            self.spectrum_s = s
        if v >= 0:
            self.spectrum_v = v
        self.colors = hsv.spectrum(self.count, self.spectrum_s, self.spectrum_v)
        if self.displayactive:
            self.showsort()

    def issorted(self):
        count = self.count
        keys = self.keys
        perm = self.perm
        for i in range(0,count-1):
            if keys[perm[i]] > keys[perm[i+1]]:
                return False
        return True

    # Swap two elements in permutation
    def swap(self, i, j, show=False):
        colors = self.colors
        cycle = self.cycle
        canvas = self.canvas
        rheight = self.rheight
        rwidth = self.rwidth
        count = self.count
        perm = self.perm
        items = self.items
        if i == j:
            return
        if i >= 0 and i < count and j >= 0 and j < count:
            (v1, v2) = (perm[i], perm[j])
            (perm[i], perm[j]) = (v2, v1)
            if show and canvas:
                c1 = colors[perm[i]]
                c2 = colors[perm[j]]
                i1 = items[i]
                i2 = items[j]
                try:
                    items[i] = canvas.create_rectangle(rwidth * i, 0,
                                                   rwidth * (i+1), rheight,
                                                   fill = '%s' % c1)
                    items[j] = canvas.create_rectangle(rwidth * (j), 0,
                                                   rwidth * (j+1), rheight,
                                                   fill = '%s' % c2)
                    canvas.delete(i1)
                    canvas.delete(i2)
                    canvas.update()
                    self.pause(int(cycle * self.cyclemult))
                except:
                    return

    # Compare two adjacent elements and swap if needed
    # Return true if swap, false if don't
    def testandswap(self, i, j, show=False):
        count = self.count
        perm = self.perm
        keys = self.keys
        if (i >= 0 and i < count
            and j >= 0 and j < count
            and keys[perm[i]] > keys[perm[j]]):
            self.swap(i, j, show)
            return True
        return False

    # Display sorted result
    def showsort(self, firsttime = False):
        colors = self.colors
        cycle = self.cycle
        canvas = self.canvas
        # Check if window has been resized:
        if not firsttime:
            curheight = self.display.winfo_height() - self.windowdeltah
            if curheight != self.rheight:
                self.rheight = curheight
                self.canvas.config(height = self.rheight)
            curwidth = self.display.winfo_width() - self.windowdeltaw
            if curwidth != self.rwidth * self.count:
                self.rwidth = curwidth / self.count
                curwidth = self.rwidth * self.count
                self.canvas.config(width = curwidth)
                if curwidth > self.swidth:
                    self.swidth = curwidth
        rheight = self.rheight
        rwidth = self.rwidth
        perm = self.perm
        keys = self.keys

        if canvas:
            for item in self.items:
                canvas.delete(item)
            self.items = []
            for i in range(0,self.count):
                color = colors[perm[i]]
                item = canvas.create_rectangle(rwidth * i, 0,
                                               rwidth * (i+1), rheight,
                                               fill = '%s' % color)
                self.items.append(item)
            canvas.update()
            self.pause(int(cycle * self.cyclemult))
        else:
            print perm
        
    # Parallel sort by swapping adjacent elements
    # Alternate between odd and even values of initial index to avoid races
    def evenoddsort(self):
        parity = 0
        while not self.issorted():
            map (lambda idx: self.testandswap(parity + 2*idx,
                                              parity + 2*idx + 1, False),
                 range(0, int(self.count/2)))
            parity = 1-parity
            self.showsort()

    # Sort 3 consecutive elements: i, i+1, i+2
    def sort3(self, i):
        self.testandswap(i, i+1, False)
        self.testandswap(i+1, i+2, False)
        self.testandswap(i, i+1, False)

    # Parallel sort by locally sorting triples.  Alternate between
    # index 4*i and 4*i+2
    def triplesort(self):
        offset = 0
        while not self.issorted():
            map (lambda idx: self.sort3(4*idx+offset),
                 range(0, int(self.count/4)))
            offset = 2-offset
            self.showsort()

    # Parallel sort by swapping pairs of elements
    # Choose pairs to have all elements disjoint
    # (Not very interesting)
    def randpairsort(self):
        while not self.issorted():
            map (lambda (i,j): self.testandswap(i, j), randpairs(self.count))
            self.showsort()

    # Selection sort
    def selectionsort(self):
        parity = False
        while not self.issorted():
            for i in range(0, self.count-1):
                idx = i if parity else self.count-i-2
                self.testandswap(idx, idx+1, True)
            parity = not parity

    # Insertion sort
    def insertionsort(self):
        # Insert i+1 into list 0:i
        for i in range(0, self.count-1):
            for idx in [i-j for j in range(0,i+1)]:
                if not self.testandswap(idx, idx+1, True):
                    break

    # Double-ended Insertion sort
    def doubleinsertionsort(self):
        # Invariant: elements [left:right] are sorted
        left = self.count/2
        right = left
        while left > 0 or right < self.count-1:
            # Insert i from left into [left:right] to get [left-1:right]
            for i in range(left-1, right-1):
                self.testandswap(i, i+1, True)
            # Insert i from right into [left-1:right] to get [left-1:right+1]
            for i in [left+right-2-j for j in range(left-2, right+1)]:
                self.testandswap(i, i+1, True)
            left = left - 1
            right = right + 1

    # Random sort
    def randomsort(self):
        while not self.issorted():
            for i in randperm(self.count-1):
                self.testandswap(i, i+1, True)

    # Swap random pairs until sorted
    def swapsort(self):
        while not self.issorted():
            (i,j) = getpair(self.count)
            self.testandswap(i, j, True)

    # Functions for quicksort
    def pivotidx(self, start, count):
        return start + count/2

    # Shift block of elements left by one position
    # Moves element formerly at start - 1 to start + len - 1
    def shiftblockleft(self, start,len):
        # Do this by Swapping leftmost element to the right
        for i in range(0, len):
            self.swap(start + i - 1, start + i, False)

    def shiftblockright(self, start,len):
        # Do this by Swapping rightmost element to the left
        for i in range(0, len):
            self.swap(start + len - i - 1, start + len - i, False)


    # Perform single step in merge sort
    # Region split into three parts: sorted, left, and right
    # Precondition: All 3 regions sorted.  All elements in sorted
    # <= those in left or right
    # Objective is to take least element from left & right
    # and move it to end of sorted.
    # Return tuple containing new values of parameters, plus flag indicating whether
    # any swaps took place
    def mergestep(self, start, ssize, lsize, rsize):
        if lsize == 0 or rsize == 0:
            return (start, ssize+lsize+rsize, 0, 0, False)
        # Compare and swap least elements in left and right
        if self.testandswap(start+ssize, start+ssize+lsize, False):
            # Value on right was less than value on left.
            # Fix by shifting left block right by one.  Will return
            # original leftmost element to position lstart+1
            self.shiftblockright(start+ssize+1,lsize-1)
            return (start, ssize+1, lsize, rsize-1, True)
        else:
            # Value on left was less than value on right.
            return (start, ssize+1, lsize-1, rsize, False)

    # Given list of pairs of form (start, len), set up merge steppers
    def makesteppers(self, ls):
        n = len(ls)
        if (n == 1):
            (start,size) = ls[0]
            return [(start, 0, size, 0)]
        if (n == 2):
            (lstart, lsize) = ls[0]
            (rstart, rsize) = ls[1]
            return([(lstart, 0, lsize, rsize)])
        else:
            hn = int((n+1)/2)
            left = self.makesteppers(ls[:hn])
            right = self.makesteppers(ls[hn:])
            return left+right

    def mergesort(self):
        # Split list into singleton sets
        todo = [(i,1) for i in range(0, self.count)]
        sortdone = False
        while not sortdone:
            # Create set of sorting steppers
            steppers = self.makesteppers(todo)
            steppingdone = False
            while not steppingdone:
                nsteppers = []
                steppingdone = True
                changes = False
                for (start, ssize, lsize, rsize) in steppers:
                    (nstart, nssize, nlsize, nrsize, change) = \
                             self.mergestep(start, ssize, lsize, rsize)
                    steppingdone = steppingdone and nlsize + nrsize == 0
                    nsteppers.append((nstart, nssize, nlsize, nrsize))
                    changes = changes or change
                if changes:
                    self.showsort()
                steppers = nsteppers
            sortdone = len(todo) == 1
            todo = [(start, ssize) for (start, ssize, lsize, rsize) in steppers]

    # Quicksort routines
    def partition(self, start, count, pivot):
        perm = self.perm
        keys = self.keys
        left = start
        right = start + count - 1
        while (True):
            while left <= right and keys[perm[left]] <= pivot:
                left = left + 1
            while left <= right and pivot <= keys[perm[right]]:
                right = right - 1
            if (left < right):
                self.swap(left, right, True)
                left = left + 1
                right = right - 1
            else:
                break
        return left

   
    # Recursive quicksort
    def rqsort(self, start=0, count=-1):
        perm = self.perm
        keys = self.keys
        if (count < 0):
            count = self.count - start
        p = self.pivotidx(start, count)
        pivot = keys[perm[p]]
        right = start + count - 1
        self.swap(p, right, True)
        middle = self.partition(start, count-1, pivot)
        self.swap(middle, right, True)
        if (middle > start):
            self.rqsort(start, middle - start)
        if (middle < right):
            self.rqsort(middle+1, right-middle)
    
    # Quicksort using list to serve as stack or queue
    # Seems like breadth-first is more interesting visually
    def qsort(self, breadth=True):
        # Each element contains (start, count) pair
        perm = self.perm
        keys = self.keys
        todo = deque([(0, self.count)])
        while len(todo) > 0:
            if breadth:
                (start, count) = todo.popleft()
            else:
                (start, count) = todo.popright()
            p = self.pivotidx(start, count)
            pivot = keys[perm[p]]
            right = start + count - 1
            self.swap(p, right, True)
            middle = self.partition(start, count-1, pivot)
            self.swap(middle, right, True)
            if (middle > start):
                ns = start
                nc = middle-start
                todo.append((ns,nc))
            if (middle < right):
                ns = middle+1
                nc = right-middle
                todo.append((ns,nc))

    # Perform single sort
    def runsort(self, method='random', order='forward', c = 10000, pause = 0):
        self.showsort()        
        count = self.count
        self.keys = pinvert(genperm(self.count, order=order))
        keys = self.keys
        self.cycle = self.cycles[method]
        if c < 10000:
            self.cycle = c
        if method == 'evenodd':
            self.evenoddsort()
#        if method == 'randpairs':
#            self.randpairsort()
        elif method == 'selection':
            self.selectionsort()
        elif method == 'insertion':
            self.insertionsort()
        elif method == 'dinsertion':
            self.doubleinsertionsort()
        elif method == 'random':
            self.randomsort()
        elif method == 'quick':
            self.qsort()
        elif method == 'swap':
            self.swapsort()
        elif method == 'triple':
            self.triplesort()
        elif method == 'merge':
            self.mergesort()
        self.lastorder = order
        if pause > 0:
            self.pause(pause)

    def choosemethod(self):
        method = randele(self.methods)
        return method

    def chooseorder(self, method='none'):
        while True:
            order = randele(orders)
            if order != self.lastorder and \
                    (method, order) not in self.taboopairs:
                return order

    def run(self, s=100):
        canvas = self.canvas
        for i in range(0,s):
            method = self.choosemethod()
            order = self.chooseorder(method = method)
            print "Sorting with method %s to get %s order" % (method, order)
            self.runsort(method=method, order=order)
            self.pause(1000)

    
 
