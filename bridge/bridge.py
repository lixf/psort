#!/usr/bin/python

# update info
# added functionality to handle remote display 
# uses Lumiverse to display on the bridge

# Top level interface for bridge lighting program

from Tkinter import *
import psort
import getopt
import sys
#include Lumiverse here
import lumiversepython

class Bridge:
    # added to support bridge mode
    remote = 

    master = []

    sorter = []
    sorteractive = False
    count = 90
    # Signal to stop after completing next sorting
    keepgoing = True
    running = False
    paused = False
    # How many total seconds for each sort
    # Change using rate slider
    time = 30
    # Border color.  Empty string means no borders
    bordercolor = ''
    # subdivisions of rectangle.  1 when no border.  >= 3 when border
    subdivisions = 1

    # Track changes to any of the sliders.  Their effects will only be
    # registered when the mouse is released.
    lastslider = 'none'

    def __init__(self, master, count = 0, subdivisions = 1,
                 border = 0):
        self.master = master
        if count > 0:
            self.count = count
        # Track all button releases
        master.bind("<ButtonRelease-1>", self.buttonreleased)

        self.subdivisions = subdivisions
        if subdivisions > 1:
            if border < 0.0 or border > 1.0:
                border = 0.0
            val = int(255 * border)
            self.bordercolor = '#%.2x%.2x%.2x' % (val,val,val)
        else:
            self.bordercolor = ''

        self.cntlframe = Frame(master)
        self.cntlframe.pack()


        self.gobutton = Button(self.cntlframe, text="Go",
                               height=3, width = 20,
                               command=self.run)
        self.gobutton.pack(side=LEFT)

        self.stopbutton = Button(self.cntlframe, text="Stop",
                                 height=3, width = 20,
                                 command=self.stop)
        self.stopbutton.pack(side=LEFT)

# Reset button is not very useful
#        self.resetbutton = Button(self.cntlframe, text="Reset",
#                                  height=3, width = 20,
#                                  command=self.init)
#        self.resetbutton.pack(side=LEFT)

        self.exitbutton = Button(self.cntlframe, text="Exit",
                                 height=3, width = 20,
                                 command=self.quit)
        self.exitbutton.pack(side=LEFT)

        self.infoframe = Frame(master)
        self.infoframe.pack()

        self.fromorderframe = Frame(self.infoframe)
        
        self.fromorderframe.pack(side=LEFT)
        self.fromordertitle = Label(self.fromorderframe, width = 15,
                                    text = 'Last ordering')
        self.fromordertitle.pack(side=TOP)
        self.fromorderlabel = Label(self.fromorderframe, width = 15,
                                    bg='white', relief=SUNKEN, justify=LEFT)
        self.fromorderlabel.pack(side=BOTTOM)

        self.toorderframe = Frame(self.infoframe)
        
        self.toorderframe.pack(side=LEFT)
        self.toordertitle = Label(self.toorderframe, width = 15,
                                    text = 'New ordering')
        self.toordertitle.pack(side=TOP)
        self.toorderlabel = Label(self.toorderframe, width = 15,
                                  bg='white', relief=SUNKEN, justify=LEFT)
        self.toorderlabel.pack(side=BOTTOM)

        self.modeframe = Frame(self.infoframe)
        
        self.modeframe.pack(side=LEFT)
        self.modetitle = Label(self.modeframe, width = 15,
                                    text = 'Display Mode')
        self.modetitle.pack(side=TOP)

        self.modelabel = Label(self.modeframe, width = 15,
                                 bg='white', relief=SUNKEN, justify=LEFT)
        self.modelabel.pack(side=LEFT)


        self.methodframe = Frame(self.infoframe)
        
        self.methodframe.pack(side=LEFT)
        self.methodtitle = Label(self.methodframe, width = 15,
                                    text = 'Sorting Method')
        self.methodtitle.pack(side=TOP)

        self.methodlabel = Label(self.methodframe, width = 15,
                                 bg='white', relief=SUNKEN, justify=LEFT)
        self.methodlabel.pack(side=LEFT)

        self.rateframe = Frame(master)
        # Track mouse button release events
#        self.rateframe.bind("<ButtonRelease-1>", self.buttonreleased)
        self.rateframe.pack()
        self.rateslider = Scale(self.rateframe, label="Sorting Rate",
                                length=300,
                                orient=HORIZONTAL, command=self.setRate)
        self.rateslider.config(from_ = -20, to = 20)
        self.rateslider.pack()

        self.countslider = Scale(self.rateframe, label="Elements",
                                 length=300,
                                 orient=HORIZONTAL, command=self.setCount)
        self.countslider.config(from_ = 2, to = 200)
        self.countslider.set(self.count)
        self.countslider.pack()

        

        self.svframe = Frame(master)
        # Track mouse button release events
#        self.svframe.bind("<ButtonRelease-1>", self.buttonreleased)
        self.svframe.pack()
        self.sslider = Scale(self.svframe, label="Saturation * 100",
                             length = 150,
                             orient=HORIZONTAL, command=self.sets)
        self.sslider.set(100)
        self.sslider.pack(side=LEFT)

        self.vslider = Scale(self.svframe, label="Value * 100",
                             length = 150,
                             orient=HORIZONTAL, command=self.setv)
        self.vslider.set(100)
        self.vslider.pack(side=LEFT)

    def init(self):
        self.keepgoing = True
        if self.sorteractive:
            saturation = self.sorter.spectrum_s
            value = self.sorter.spectrum_v
            self.sorter.quit()
            self.sorter = psort.Psort(n = self.count,
                                      saturation = saturation,
                                      value = value,
                                      subdivisions = self.subdivisions,
                                      bordercolor = self.bordercolor)
        else:
            self.sorter = psort.Psort(self.count,
                                      subdivisions = self.subdivisions,
                                      bordercolor = self.bordercolor)
        self.sorteractive = True

    def run(self):
        if not self.sorteractive:
            self.init()
        self.keepgoing = True

        self.running = True
        # Don't allow row mode changes on first iteration
        changeok = False
        while self.keepgoing:
            lastorder = self.sorter.lastorder
            self.fromorderlabel.config(text=lastorder)
            mode = self.sorter.rowmode
            if changeok:
                mode = self.sorter.choosemode()
            changeok = True
            self.modelabel.config(text=mode)
            method = self.sorter.choosemethod(mode=mode)
            self.methodlabel.config(text=method)
            order = self.sorter.chooseorder(method=method)
            self.toorderlabel.config(text=order)
            self.sorter.runsort(method=method, order=order, time = self.time, pause=2000)

    def stop(self):
        self.keepgoing = False
        self.running = False
        # Signal sorter to accelerate
        if self.sorteractive:
            self.sorter.accelerate = True
    
    # For all of the sliders and for quit button, just record that event has occurred.
    # Don't respond until mouse button is released

    def quit(self):
        self.lastslider = 'quit'

    def setRate(self, e):
        self.lastslider = 'rate'

    def setCount(self, e):
        if self.sorteractive:
            self.lastslider = 'count'
        else:
            self.count = self.countslider.get()

    def sets(self, e):
        self.lastslider = 'saturation'

    def setv(self, e):
        self.lastslider = 'value'

    # Handle events when button is released in one of the sliders
    # or due to window resizing
    def buttonreleased(self, e):
        if not self.sorteractive:
            return
        if self.lastslider == 'quit':
            self.stop()
            # self.master.unbind("<ButtonRelease-1>")
            if self.sorteractive:
                self.sorteractive = False
                self.sorter.quit()
            self.master.destroy()
            return
        elif self.lastslider == 'rate':
            rate = self.rateslider.get()
            if self.sorter:
                self.sorter.cyclemult = 0.1**(rate/10.0)
        elif self.lastslider == 'count':
            val = self.countslider.get()
            self.count = val
            if self.sorteractive:
                saturation = self.sorter.spectrum_s
                value = self.sorter.spectrum_v
                self.sorter.quit()
                self.sorter = psort.Psort(n = self.count,
                                          saturation = saturation,
                                          value = value,
                                          subdivisions = self.subdivisions,
                                          bordercolor = self.bordercolor)
        elif self.lastslider == 'saturation':
            val = self.sslider.get()
            self.sorter.set_spectrum(s = val / 100.0)
        elif self.lastslider == 'value':
            val = self.vslider.get()
            self.sorter.set_spectrum(v = val / 100.0)
        self.sorter.showsort()
        self.lastslider = 'none'

def usage(name):
    print 'Usage: %s [-h] -c C [-r host[:port]] [-s S [-b B]]' % name
    print '   -h    Print this message'
    print '   -c C  Display C columns'
    print '   -r host[:port]  Display results on remote host'
    print '   -s S  Subdivide rectangle into s subrectangles (s >= 3)'

def run(name, args):
    cols = 90
    border = 0
    subdivisions = 1
    optlist, args = getopt.getopt(args, 'hc:s:b:')
    for (opt,val) in optlist:
        if opt == '-h':
            usage(name)
            return
        elif opt == '-c':
            cols = int(val)
        elif opt == '-b':
            border = float(val)
        elif opt == '-s':
            subdivisions = int(val)
        else:
            usage(name)
            return

    print "Creating bridge with %d columns" % cols
    if (subdivisions > 1):
        print "Subdivide rectangle into % d subrectangles.  Border color = %f" % (subdivisions, border)
    root = Tk()

    bridge = Bridge(root, cols, subdivisions, border)
    try:
        root.mainloop()
    except:
        exit()


run(sys.argv[0], sys.argv[1:])

