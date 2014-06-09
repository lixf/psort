import random
import hsv
import math
from collections import deque
import panel
import coeffs

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

# Flip a biased coin
def randflip(p=0.5):
    x = random.random()
    return x < p

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
# revfwd: From high to low and back to high
# fwdrev: From low to high and back to low
# random: Random permutation
# Interleave: Forward wrapped back on itself
orders = ['forward', 'reverse',
          'fwdrev', 'revfwd',
          'random', 'interleave'
          ]
# These orders did not prove very interesting
#          , 'fwdfwd', 'revrev'

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

# Table to translate from normal order to special
# ones used in rightleft mode
rightleftorders = {'forward':'fwdrev',
                   'reverse':'revfwd'
                   }

def fixorder(order, rowmode='single'):
    if rowmode == 'rightleft' and order in rightleftorders.keys():
        return rightleftorders[order]
    return order

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
    # Numbers: rcount = ecount * cgranularity * rgranularity * mgranularity,
    # where rgranularity depends on row mode
    # Number of elements being sorted
    ecount = 0
    # Number of rectangles in display
    rcount = 0
    # Number of columns per element
    cgranularity = 1
    # Number of copies due to mirroring
    mgranularity = 1
    # Number of subrectangles per rectangle (1 = no border. >= 3 for border)
    subdivisions = 1
    # If bordercolor != '', then have rectangle of neutral color
    # between each pair of colored rectangles
    bordercolor = ''
    # What kind of rows?
    # Possible values: single, zipper, rightleft
    rowmode = 'single'


    # Count number of update steps
    stepcount = 0
    # perm indicates permutation of values
    perm = []
    # Keys controls effect of sorting.  Is also a permutation
    keys = []
    # Colors a fixed spectrum of colors
    colors = []

    # Panel shows rectangles
    panel = []
    # Time step.  Changes based on sorting method
    cycle = 1
    # Multiplier for time step.  Can change using rate slider.
    cyclemult = 1.0
    # Set to False to pause sorter
    running = True
    # At what degree of column granularity should we do blended transitions?
    blendgranularity = 6
    # Accelerate to end of sort?
    accelerate = False

    # Keep track of last ordering
    lastorder = 'none'
    # saturation and value for spectrum
    spectrum_s = 1.0
    spectrum_v = 1.0

    # What combinations of sorting method, row mode, and target order
    # should be excluded for not being visually appealing
    taboopairs = set([
        # Sort method + target order
        ('merge', 'random'),
        ('selection', 'random'),
        ('insertion', 'random'),
        ('dinsertion', 'random'),
        ('quick', 'random'),
        # Row mode + target order
        ('zipper', 'random'),
        ('zipper', 'interleave'),
        ('rightleft', 'fwdrev'),
        ('rightleft', 'revfwd'),
        ('rightleft', 'random'),
        ('rightleft', 'interleave'),
        # Row mode + Sort method 
        ('zipper', 'evenodd'),
        ('zipper', 'triple')
        ])

    # Mapping from sort method to prediction of cycle count.
    # Includes trend plus coefficient.
    cycles = {'evenodd'   : [0.00, 0.95, 0.00, 0.00],
              'triple'    : [0.00, 0.70, 0.00, 0.00],
              'merge'     : [0.00, 1.00, 0.00, 0.00],
              'selection' : [0.00, 0.00, 0.00, 0.25],
              'insertion' : [0.00, 0.00, 0.00, 0.25],
              'dinsertion': [0.00, 0.00, 0.00, 0.25],
              'random'    : [0.00, 0.00, 0.00, 0.25],
              'quick'     : [0.00, 0.00, 0.25, 0.00],
              'swap'      : [0.00, 0.00, 0.50, 0.00],
              }

    # Sorting methods
    methods = cycles.keys()

    # n determines number of elements
    def __init__(self, n=48, order='forward', saturation = 0, value = 0,
                 rhost = '', subdivisions = 1, bordercolor = '', nodisplay = False):
        self.ecount = n
        self.rowmode = 'single'
        self.cgranularity = 1
        self.mgranularity = 1
        self.subdivisions = subdivisions
        if subdivisions > 1 and not bordercolor:
            bordercolor = '#000000'
        self.bordercolor = bordercolor
        self.rcount = n * 2 * self.subrectanglecount(True) * self.mgranularity
        self.perm = genperm(n, order=order)
        self.keys = range(0, n)
        self.lastorder = order
        cols = self.rcount/2
        self.panel = panel.Panel(rows = 2, cols = cols,
                                 rwidth = int(1440/cols), nodisplay = nodisplay)
        if rhost:
            port = 8000
            (host, s, p) = rhost.partition(':')
            if p:
                port = int(p)
            pn = panel.PanelClient(host, port)
            self.panel.addsubpanel(pn)
        if saturation > 0:
            self.spectrum_s = saturation
        if value > 0:
            self.spectrum_v = value
        self.colors = hsv.spectrum(n, self.spectrum_s, self.spectrum_v,
                                   granularity=self.colorgranularity(self.rowmode))
        self.showsort()

    # Change column granularity.  Also used when changing row mode
    def setcgranularity(self, c=1):
        self.cgranularity = c
        n = int(self.rcount /
                (self.rgranularity(self.rowmode) * self.subrectanglecount(True) * self.mgranularity))
        self.ecount = n
        if self.lastorder == 'none':
            self.lastorder = 'forward'
        self.perm = genperm(n,
                            order=fixorder(self.lastorder, self.rowmode))
        self.keys = range(0, n)
        self.colors = hsv.spectrum(n, self.spectrum_s, self.spectrum_v,
                                   granularity=self.colorgranularity(self.rowmode))
        self.showsort()

    # Change degree of mirroring
    # No-op if conditions are not right
    def setmgranularity(self, m = 1):
        n = self.ecount
        curm = self.mgranularity
#        print 'Changing mgranularity from %d to %d' % (curm, m)
        if m == 2 * curm:
            # Double degree of mirroring (mirror2)
            n = n / 2
            if self.lastorder == 'fwdrev':
                self.lastorder = 'forward'
            elif self.lastorder == 'revfwd':
                self.lastorder = 'reverse'
            else:
                print 'Invalid order for mirroring'
                return # Invalid order for mirroring
        elif m * 2 == curm:
            # Halve degree of mirroring (unmirror2)
            n = n * 2
            if self.lastorder == 'forward':
                self.lastorder = 'fwdrev'
            elif self.lastorder == 'reverse':
                self.lastorder = 'revfwd'
            else:
                print 'Invalid order for unmirroring'
                return # Invalid order for unmirroring
        self.ecount = n
        self.mgranularity = m
        self.perm = genperm(n,
                            order=fixorder(self.lastorder, self.rowmode))
        self.keys = range(0, n)
        self.colors = hsv.spectrum(n, self.spectrum_s, self.spectrum_v,
                                   granularity=self.colorgranularity(self.rowmode))
        self.showsort()


    # Determine how many subrectangles comprise single rectangle
    # If fullwidth, then considers border subrectangles, as well
    def subrectanglecount(self, fullwidth = False):
        val = self.subdivisions * self.cgranularity
        if self.subdivisions > 1 and not fullwidth:
            val = val - 1
        return val

    # Delay for specified amount of time (ms)
    def pause(self, t):
        if self.panel != [] and t > 0:
            self.panel.after(t)

    def quit(self, killsubpanels = True):
        if self.panel != []:
            self.accelerate = True;
            panel = self.panel
            self.panel = []
            check = panel.quit(killsubpanels)
            self.panel = []

    def set_spectrum(self, s = -1, v = -1):
        if s >= 0:
            self.spectrum_s = s
        if v >= 0:
            self.spectrum_v = v
        self.colors = hsv.spectrum(self.ecount, self.spectrum_s, self.spectrum_v,
                                   granularity=self.colorgranularity(self.rowmode))
        self.showsort()

    def issorted(self):
        count = self.ecount
        keys = self.keys
        perm = self.perm
        for i in range(0,count-1):
            if keys[perm[i]] > keys[perm[i+1]]:
                return False
        return True

    # Swap two elements in permutation
    def swap(self, i, j, show=False):
        count = self.ecount
        mcount = self.mgranularity
        perm = self.perm
        if i == j:
            return
        if i >= 0 and i < count and j >= 0 and j < count:
            (v1, v2) = (perm[i], perm[j])
            (perm[i], perm[j]) = (v2, v1)
            if not self.accelerate and show and self.panel != []:
                c1 = self.colors[perm[i]]
                c2 = self.colors[perm[j]]
                if c1 != c2:
                    ls = []
                    for m in range(0,mcount):
                        (ri,ci,hi,wi) = self.rchwpos(i,m)
                        (rj,cj,hj,wj) = self.rchwpos(j,m)
                        ls.append((ri,ci,c1,hi,wi))
                        ls.append((rj,cj,c2,hj,wj))
                    delay = int(self.cycle * self.cyclemult)
                    check = self.panel.paintlist(ls, delay = delay,
                                                 blend = self.cgranularity >= self.blendgranularity)
                    self.stepcount = self.stepcount + 1

    # Compare two adjacent elements and swap if needed
    # Return true if swap, false if don't
    def testandswap(self, i, j, show=False):
        count = self.ecount
        perm = self.perm
        keys = self.keys
        if (i >= 0 and i < count
            and j >= 0 and j < count
            and keys[perm[i]] > keys[perm[j]]):
            self.swap(i, j, show)
            return True
        return False

    # Define granularity of colors
    def colorgranularity(self, mode):
        if mode == 'single':
            return 1
        elif mode == 'zipper':
            return 4
        else:
            return 2

    # Determine number of rows each element uses
    def rgranularity(self, mode):
        if mode == 'single':
            return 2
        return 1


    # Determine row, column, width, and height of rectangle, given index and mirror index
    def rchwpos(self, i, m = 0):
        w = self.subrectanglecount(False)
        h = self.rgranularity(self.rowmode)
        n = self.ecount
        s = self.subrectanglecount(True)
        mcount = self.mgranularity
        # Width (in elements) of one complete copy
        mwidth = n*h/2
        # Compute ci: index of column
        if self.rowmode == 'zipper':
            ci = int(i/2)
            r = (ci + i) % 2
        elif self.rowmode == 'rightleft':
            if i < n/2:
                ci = i
                r = 0
            else:
                ci = n - 1 - i
                r = 1
        else: # 'single'
            r = 0
            ci = i
        # Adjust column based on which mirrored copy this is
        mci = m * mwidth + (ci if m % 2 == 0 else mwidth-1-ci)
        # Scale by number of rectangles in each element
        c = mci * s
#        print 'rchw(%d,%d) --> (%d,%d,%d,%d) (mwidth = %d)' % (i,m,r,c,h,w,mwidth)
        return (r,c,h,w)

    # Display sorted result
    def showsort(self):
        colors = self.colors
        cycle = self.cycle
        perm = self.perm
        keys = self.keys
        panel = self.panel
        count = self.ecount
        mcount = self.mgranularity

        # Operating in accelerated mode
        if self.accelerate:
            return

        if panel != []:
            ls = []
            # Put in border color, if necessary
            if self.bordercolor:
                h = 2
                w = self.rcount / h
                ls.append((0,0,self.bordercolor,h,w))
            for i in range(0,count):
                color = colors[perm[i]]
                for m in range(0,mcount):
                    (r,c,h,w) = self.rchwpos(i,m)
                    ls.append((r,c,color,h,w))

            delay = int(self.cycle * self.cyclemult)
            check = self.panel.paintlist(ls, delay = delay,
                                         blend = self.cgranularity >= self.blendgranularity)
            self.stepcount = self.stepcount + 1

        
    # Parallel sort by swapping adjacent elements
    # Alternate between odd and even values of initial index to avoid races
    def evenoddsort(self):
        parity = 0
        change = [True, True]
        while change[0] or change[1]:
            sorts = \
            map (lambda idx:
                 self.testandswap(parity + 2*idx,
                                              parity + 2*idx + 1, False),
                 range(0, int(self.ecount/2)))
            change[parity] = reduce(lambda x,y: x or y, sorts)
            if change[parity]:
                self.showsort()
            parity = 1-parity

    # Sort 3 consecutive elements: i, i+1, i+2
    def sort3(self, i):
        change1 = self.testandswap(i, i+1, False)
        change2 = self.testandswap(i+1, i+2, False)
        change3 = change2 and self.testandswap(i, i+1, False)
        return change1 or change2 or change3

    # Parallel sort by locally sorting triples.  Alternate between
    # index 4*i and 4*i+2
    def triplesort(self):
        change = [True, True]
        parity = 0
        while change[0] or change[1]:
            sorts = \
            map (lambda idx: self.sort3(4*idx+parity*2),
                 range(0, 1+int(self.ecount/4)))
            change[parity] = reduce(lambda x, y: x or y, sorts)
            if change[parity]:
                self.showsort()
            parity = 1-parity

    # Parallel sort by swapping pairs of elements
    # Choose pairs to have all elements disjoint
    # (Not very interesting)
    def randpairsort(self):
        while not self.issorted():
            map (lambda (i,j): self.testandswap(i, j), randpairs(self.ecount))
            self.showsort()

    # Selection sort
    def selectionsort(self):
        parity = False
        while not self.issorted():
            for i in range(0, self.ecount-1):
                idx = i if parity else self.ecount-i-2
                self.testandswap(idx, idx+1, True)
            parity = not parity

    # Insertion sort
    def insertionsort(self):
        # Insert i+1 into list 0:i
        for i in range(0, self.ecount-1):
            for idx in [i-j for j in range(0,i+1)]:
                if not self.testandswap(idx, idx+1, True):
                    break

    # Double-ended Insertion sort
    def doubleinsertionsort(self):
        # Invariant: elements [left:right] are sorted
        left = self.ecount/2
        right = left
        while left > 0 or right < self.ecount-1:
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
            for i in randperm(self.ecount-1):
                self.testandswap(i, i+1, True)

    # Swap random pairs until sorted
    def swapsort(self):
        while not self.issorted():
            (i,j) = getpair(self.ecount)
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
        todo = [(i,1) for i in range(0, self.ecount)]
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
            count = self.ecount - start
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
        todo = deque([(0, self.ecount)])
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

    # Choose and set rowmode.  Return mode
    def choosemode(self):
        # Stay the same 50% of the time
        curmode = self.rowmode
        if randflip(0.5):
            return curmode
        # Otherwise, collect list of possibilities
        lastorder = self.lastorder
        # Which orders can be in place when change resolution
        changeorders = ['forward', 'reverse', 'fwdrev', 'revfwd']
        nextmode = []
        # Changes that don't change horizontal resolution
        for newmode in ['single', 'rightleft', 'zipper']:
            newrem = (self.ecount * self.rgranularity(curmode)) % self.rgranularity(newmode)
            newecount = (self.ecount * self.rgranularity(curmode)) / self.rgranularity(newmode)
            ncrem = newecount % self.colorgranularity(newmode)
            ncolor = newecount / self.colorgranularity(newmode)
            # Must make sure that number of elements is integral, divisible by the color granularity
            # and that there's more than one color
            if (curmode != newmode and 
                (newmode, lastorder) not in self.taboopairs and
                newrem == 0 and ncrem == 0 and ncolor > 1):
                nextmode.append(newmode)
        # Refinement
        if lastorder in changeorders and self.cgranularity % 2 == 0:
            nextmode.append('refine2')
        if lastorder in changeorders and self.cgranularity % 3 == 0:
            nextmode.append('refine3')
        # Coalescing: New ecount must be multiple of color granularity and must have more than one color
        if (lastorder in changeorders and self.ecount % (2 * self.colorgranularity(curmode)) == 0
            and self.ecount / (2 * self.colorgranularity(curmode)) > 1):
            nextmode.append('coalesce2')
        if (lastorder in changeorders and self.ecount % 3 == 0
            and self.ecount / (3 * self.colorgranularity(curmode)) > 1):
            nextmode.append('coalesce3')
        # Mirroring
        if (self.ecount % 2 == 0 and
            (lastorder == 'fwdrev' or lastorder == 'revfwd')
            and (curmode == 'single' or curmode == 'zipper')):
            nextmode.append('mirror2')
        # Unmirroring
        if (self.mgranularity % 2 == 0 and
            (lastorder == 'forward' or lastorder == 'reverse')
            and (curmode == 'single' or curmode == 'zipper')):
            nextmode.append('unmirror2')
        if len(nextmode) == 0:
            # No options
            return curmode
#        print 'Possible modes: %s' % nextmode
        mode = randele(nextmode)
#        print 'Choose %s from possible modes: %s' % (mode, nextmode)
        if mode == 'refine2':
            self.setcgranularity(self.cgranularity / 2)
        elif mode == 'refine3':
            self.setcgranularity(self.cgranularity / 3)
        elif mode == 'coalesce2':
            self.setcgranularity(self.cgranularity * 2)
        elif mode == 'coalesce3':
            self.setcgranularity(self.cgranularity * 3)
        elif mode == 'mirror2':
            self.setmgranularity(self.mgranularity * 2)            
        elif mode == 'unmirror2':
            self.setmgranularity(self.mgranularity / 2)
        else:
            self.rowmode = mode
            self.setcgranularity(self.cgranularity)
        return self.rowmode

    # Estimate number of steps for next sorting operation
    def stepestimate(self, method, ekey = ''):
        # Estimate based on set of four coefficients, giving
        # constant, linear, nlogn, and quadratic functions of number of elements
        if ekey and ekey in coeffs.cyclecoeffs:
            # Compute estimate based on regression computation
            coeff = coeffs.cyclecoeffs[ekey]
        else:
            # Compute estimate based on method only
            coeff = self.cycles[method]
        estimate = coeff[0] + self.ecount * (coeff[1] + math.log(self.ecount) * coeff[2] + self.ecount * coeff[3])
        return int(round(estimate))


    # Perform single sort
    def runsort(self, method='random', order='forward', time = 60, pause = 0, log = False, phase = 0):
        self.showsort()        
        count = self.ecount
        lastorder = fixorder(self.lastorder, self.rowmode)
        neworder = fixorder(order, self.rowmode)
        self.keys = pinvert(genperm(self.ecount, order=neworder))
        keys = self.keys
        ekey = '%s+%s+%s+%s' % (method, lastorder, neworder, self.rowmode)
        esteps = self.stepestimate(method, ekey)
        if esteps < 1:
            esteps = 1
        self.cycle = int(1000.0 * time / esteps)
        if self.cycle < 1:
            self.cycle = 1
        self.stepcount = 0

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
        if log:
            asteps = self.stepcount
            err = float(esteps - asteps) / (0.5 * float(esteps + asteps))
            if err < 0:
                err = -err
            print '%d\t%d\t%s\t%s\t%s\t%s\t%d\t%d\t%.2f' % \
            (phase, self.ecount, method, lastorder, neworder, self.rowmode, esteps, asteps, err)

        # Complete accelerated operation
        if self.accelerate:
            self.accelerate = False
            self.showsort()
        self.pause(pause)

    def choosemethod(self, mode = 'none'):
        while True:
            method = randele(self.methods)
            if (mode, method) not in self.taboopairs:
                return method

    def chooseorder(self, method='none'):
        while True:
            order = randele(orders)
            if order != self.lastorder and \
                    (method, order) not in self.taboopairs and \
                    (self.rowmode, order) not in self.taboopairs:
                return order

    def run(self, s=100, time = 60, log = False):
        if log:
            print 'Phase\tElements\tmethod\toldorder\tneworder\trowmode\testeps\tasteps\terr'
        for i in range(0,s):
            lastorder = self.lastorder
            mode = self.choosemode()
            method = self.choosemethod(mode)
            order = self.chooseorder(method = method)
            reallastorder = fixorder(lastorder, mode)
            realorder = fixorder(order, mode)
            if not log:
                print "Sorting %d elements with method %s to get %s order in row mode %s with %d mirrored copies" % \
                      (self.ecount, method, order, mode, self.mgranularity)
            pause = 0 if log else 1000
            self.runsort(method=method, order=order, time = time, pause = pause, log = log, phase = i+1)

    
 
