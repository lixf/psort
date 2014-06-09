#!/usr/bin/python
# Top level interface for bridge lighting program

from Tkinter import *
import psort

class Bridge:
    master = []
    sorter = []
    sorteractive = False
    count = 40
    # Signal to stop after completing next sorting
    keepgoing = True
    running = False
    # Used to temporarily store cycle multiplier rate when stopping
    savecyclemult = 1.0

    # Track changes to any of the sliders.  Their effects will only be
    # registered when the mouse is released.
    lastslider = 'none'

    def __init__(self, master):
        self.master = master
        # Track all button releases
        master.bind("<ButtonRelease-1>", self.buttonrelease)

        self.cntlframe = Frame(master)
        self.cntlframe.pack()


        self.gobutton = Button(self.cntlframe, text="Go",
                               height=3, width = 15,
                               command=self.run)
        self.gobutton.pack(side=LEFT)

        self.stopbutton = Button(self.cntlframe, text="Stop",
                                 height=3, width = 15,
                                 command=self.stop)
        self.stopbutton.pack(side=LEFT)

# Reset button is not very useful
#        self.resetbutton = Button(self.cntlframe, text="Reset",
#                                  height=3, width = 15,
#                                  command=self.init)
#        self.resetbutton.pack(side=LEFT)

        self.exitbutton = Button(self.cntlframe, text="Exit",
                                 height=3, width = 15,
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
#        self.rateframe.bind("<ButtonRelease-1>", self.buttonrelease)
        self.rateframe.pack()
        self.rateslider = Scale(self.rateframe, label="Sorting Rate",
                                length=300,
                                orient=HORIZONTAL, command=self.setRate)
        self.rateslider.config(from_ = -20, to = 20)
        self.rateslider.pack()

        self.countslider = Scale(self.rateframe, label="Elements",
                                 length=300,
                                 orient=HORIZONTAL, command=self.setCount)
        self.countslider.config(from_ = 2, to = 100)
        self.countslider.set(self.count)
        self.countslider.pack()

        self.svframe = Frame(master)
        # Track mouse button release events
#        self.svframe.bind("<ButtonRelease-1>", self.buttonrelease)
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
            width = self.sorter.swidth
            height = self.sorter.rheight
            self.sorter.quit()
            self.sorter = psort.Psort(n = self.count, saturation = saturation,
                                      value = value, height = height, width = width)
        else:
            self.sorter = psort.Psort(self.count)
        self.sorteractive = True

    def run(self):
        if not self.sorteractive:
            self.init()
        self.keepgoing = True

        self.running = True
        while self.keepgoing:
            lastorder = self.sorter.lastorder
            self.fromorderlabel.config(text=lastorder)
            method = self.sorter.choosemethod()
            self.methodlabel.config(text=method)
            order = self.sorter.chooseorder(method=method)
            self.toorderlabel.config(text=order)
            self.sorter.runsort(method=method, order=order, pause=2000)
        # Restore cycle multipler in event that it was
        # set to 0 do to a click of the stop button
        self.sorter.cyclemult = self.savecyclemult

    def stop(self):
        self.keepgoing = False
        self.running = False
        # Accelerate sorting by setting cycle multipler to 0.
        if self.sorteractive and self.sorter.cyclemult > 0:
            self.savecyclemult = self.sorter.cyclemult
            self.sorter.cyclemult = 0

    def quit(self):
        self.stop()
        self.master.unbind("<ButtonRelease-1>")
        if self.sorteractive:
            self.sorter.quit()
        self.master.destroy()

    # For all of the sliders, just record that event has occurred.
    # Don't respond until mouse button is released
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
    def buttonrelease(self, e):
        if not self.sorteractive:
            return
        if self.lastslider == 'rate':
            val = self.rateslider.get()
            self.sorter.cyclemult = 0.1**(val/10.0)
        elif self.lastslider == 'count':
            val = self.countslider.get()
            self.count = val
            if self.sorteractive:
                self.sorter.newcount(val)
            if self.running:
                self.run()
        elif self.lastslider == 'saturation':
            val = self.sslider.get()
            self.sorter.set_spectrum(s = val / 100.0)
        elif self.lastslider == 'value':
            val = self.vslider.get()
            self.sorter.set_spectrum(v = val / 100.0)
        self.sorter.showsort()
        self.lastslider = 'none'

root = Tk()

bridge = Bridge(root)

try:
    root.mainloop()
except:
    exit()



