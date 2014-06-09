from Tkinter import *
import hsv


# Are two values within some tolerance of each other?
def outofrange(x, y, delta):
    if x + delta < y or x - delta > y:
        return True
    return False

# Display grid of rectangles, with changing colors for each

class Panel:
    # Global state
    rows = 2
    cols = 40
    rwidth = 40
    rheight = 200
    # Possible to put items on queue rather than displaying directly
    queuevals = False
    itemqueue = []
    # What is total time to display all queued items
    queuedtime = 0
    # Difference between window height/width and image (determined empirically)
    windowdelta = 4
    # Screen size
    swidth = 0
    sheight = 0
    # Display is TK window
    display = []
    # Canvas is canvas within display
    canvas = []
    # The set of rectangles, in row-major order with (0,0) being top left
    items = []

    # Determine index of given rectangle
    def index(self, r, c):
        return r * self.cols + c

    # Determine left x, bottom y of rectangle
    # given row and column
    def xypos(self, r, c):
        rwidth = self.rwidth
        rheight = self.rheight
        x = rwidth * c
        y = rheight * r
        return (x, y)

    def __init__(self, rows=0, cols=0, rwidth = 0, rheight = 0, nodisplay = False, queuevals = False):
        if rows > 0:
            self.rows = rows
        if cols > 0:
            self.cols = cols
        if rwidth > 0:
            self.rwidth = rwidth
        if rheight > 0:
            self.rheight = rheight
        self.items = []
        self.queuevals = queuevals
        self.itemqueue = []
        self.queuedtime = 0
        if nodisplay:
             self.display = []
             return
        self.display = Tk()
        self.display.title('Displaying %d X %d rectangles'
                           % (self.rows, self.cols))
        self.frame = Frame(self.display)
        self.frame.pack(fill=BOTH, expand=YES)
        self.canvas = Canvas(self.frame,
                             width=self.rwidth * self.cols,
                             height=self.rheight * self.rows,
                             background="#ffffff")
        self.canvas.pack(fill=BOTH, expand=YES)
        self.canvas.grid(row=0, column=0)
        for r in range(0, self.rows):
            for c in range(0, self.cols):
                (x, y) = self.xypos(r, c)
                w = self.rwidth
                h = self.rheight
                self.items.append(self.canvas.create_rectangle(x, y, x + w, y + h,
                                                               width = 0, fill = '#ffffff'))
                
    def resize(self, swidth, sheight):
        self.swidth = swidth
        self.sheight = sheight
        self.rwidth = int(swidth/self.cols)
        self.rheight = int(sheight/self.rows)
        if not self.display:
             return
        canvas = self.canvas
        canvas.config(height = self.rows * self.rheight)
        canvas.config(width = self.cols * self.rwidth)
        for r in range(0, self.rows):
             for c in range(0, self.cols):
                  index = self.index(r, c)
                  (x, y) = self.xypos(r, c)
                  w = self.rwidth
                  h = self.rheight
                  oldrect = self.items[index]
                  color = canvas.itemconfig(oldrect, "fill")[-1]
                  self.items[index] = \
                                    canvas.create_rectangle(x, y, x + w, y + h, fill = color, width = 0)
                  canvas.delete(oldrect)

    def setrowcol(self, rows = 0, cols = 0):
         if rows == self.rows and cols == self.cols:
              return 1
         self.swidth = self.cols * self.rwidth
         self.sheight = self.rows * self.rheight
         if rows > 0:
              self.rows = rows
         if cols > 0:
              self.cols = cols
         self.rwidth = int(self.swidth / self.cols)
         self.rheight = int(self.sheight / self.rows)
         if self.display:
              self.canvas.delete(ALL)
         self.items = []
         for r in range(0, self.rows):
              for c in range(0, self.cols):
                   (x, y) = self.xypos(r, c)
                   w = self.rwidth
                   h = self.rheight
                   self.items.append(self.canvas.create_rectangle(x, y, x + w, y + h,
                                                               width = 0, fill = '#ffffff'))
         return 1

    # Get list of current colors
    def getstate(self):
         return map (lambda item:
                            self.canvas.itemconfig(item, "fill")[-1],
                     self.items)

    def paint(self, r, c, color = '#ffffff', rowcount = 1, colcount = 1):
         if self.queuevals:
              self.itemqueue.append(('paint', r, c, color, rowcount, colcount))
              return 1
         if (self.display and
             r >= 0 and r+rowcount <= self.rows and
             c >= 0 and c+colcount <= self.cols):
              for row in range(r, r+rowcount):
                   for col in range(c, c+colcount):
                        index = self.index(row, col)
                        (x, y) = self.xypos(row, col)
                        w = self.rwidth
                        h = self.rheight
                        rect = self.items[index]
                        self.canvas.itemconfig(rect, fill = color)
         return 1

    # Like paint, except given entire list of tuples
    # Tuple form: (r, c, color, rowcount, colcount)
    # When delay > 0, potentially do transition from current color to new ones
    def paintlist(self, ls, delay = 0, blend = False):
         # Time increment for each transition step
         transitiondelta = 50
         # Maximum fraction of time for transition
         transitionfraction = 0.25
         # What is maximum transition time
         transitiontime = 2000
         steps = int(transitiontime / transitiondelta)
         if transitiontime >= delay * transitionfraction:
              transitiontime = delay * transitionfraction
              steps = int(transitiontime / transitiondelta)
         if blend and steps > 1:
              # Capture starting colors
              startstate = self.getstate()
         for t in ls:
              (r, c, color, rowcount, colcount) = t
              self.paint(r, c, color, rowcount, colcount)
         if (delay > 0):
              if blend and steps > 1:
                   # Capture target colors
                   targetstate = self.getstate()
                   i = 1
                   while i <= steps:
                        nextstate = map (lambda c1, c2:
                                         hsv.blend(c2, c1, float(i) / steps),
                                         startstate, targetstate)
                        map (lambda item, color:
                             self.canvas.itemconfig(item, fill = color),
                             self.items, nextstate)
                        i = i+1
                        self.update(transitiondelta)
                        delay = delay - transitiondelta
              self.update(delay)
         return len(ls)

    def update(self, delay = 0):
         if self.queuevals:
              self.itemqueue.append(('update', delay))
              self.queuedtime = self.queuedtime + delay
              return 1
         if self.display == []:
              return 1
         cursheight = self.display.winfo_height() - self.windowdelta
         curswidth = self.display.winfo_width() - self.windowdelta
         if self.swidth == 0 and self.sheight == 0:
              self.swidth = curswidth
              self.sheight = cursheight
         elif outofrange(cursheight, self.sheight, 5) \
                  or outofrange(curswidth, self.swidth, 5):
              self.resize(curswidth, cursheight)
         self.canvas.update()
         if delay > 0:
              self.after(delay)
         return 1

    # Show all items in queue.  Adjust delays to match total time (in ms)
    def showqueue(self, totaltime = 10000, itemqueue = [], queuedtime = 0):
         if not itemqueue:
              itemqueue = self.itemqueue
              queuedtime = self.queuedtime
         # Temporarily disable queuing of items
         self.itemqueue = []
         self.queuedtime = 0
         savequeuevals = self.queuevals
         self.queuevals = False
         # How much to adjust individual delays
         timefactor = 1.0 if queuedtime == 0 else float(totaltime) / queuedtime
         print 'Adjusting time by %.2f to complete total %d within time %d' % \
               (timefactor, queuedtime, totaltime)
         for t in itemqueue:
              cmd = t[0]
              if (cmd == 'paint'):
                   self.paint(t[1], t[2], t[3], t[4], t[5])
              if (cmd == 'update'):
                   delay = int(float(t[1]) * timefactor)
                   self.update(delay)
         print 'done'
         self.queuevals = savequeuevals
             
    
    def quit(self):
        display = self.display
        self.display = []
        if display:
             self.canvas.quit()
             display.destroy()

    def after(self, t):
        if self.display != []:
             self.display.after(t)

        

