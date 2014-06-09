#!/usr/bin/python

from Tkinter import *
import psort

class Gui:
    master = []
    sorter = []
    sorteractive = False
    count = 40
    keepgoing = True
    # Used to temporarily store cycle multiplier rate when stopping
    savecyclemult = 1.0

    def __init__(self, master):
        self.master = master
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

        self.resetbutton = Button(self.cntlframe, text="Reset",
                                  height=3, width = 15,
                                  command=self.init)
        self.resetbutton.pack(side=LEFT)

        self.exitbutton = Button(self.cntlframe, text="Exit",
                                 height=3, width = 15,
                                 command=self.quit)
        self.exitbutton.pack(side=LEFT)

        self.infoframe = Frame(master)
        self.infoframe.pack()

        self.fromorderlabel = Label(self.infoframe, width = 20,
                                    bg='white', relief=SUNKEN, justify=LEFT)
        self.fromorderlabel.pack(side=LEFT)

        self.toorderlabel = Label(self.infoframe, width = 20,
                                  bg='white', relief=SUNKEN, justify=LEFT)
        self.toorderlabel.pack(side=LEFT)

        self.methodlabel = Label(self.infoframe, width = 20,
                                 bg='white', relief=SUNKEN, justify=LEFT)
        self.methodlabel.pack(side=LEFT)

        self.rateframe = Frame(master)
        self.rateframe.pack()
        self.rateslider = Scale(self.rateframe, label="Sorting Rate",
                                length=200,
                                orient=HORIZONTAL, command=self.setRate)
        self.rateslider.config(from_ = -20, to = 20)
        self.rateslider.pack()
        self.countslider = Scale(self.rateframe, label="Elements",
                                 length=200,
                                 orient=HORIZONTAL, command=self.setCount)
        self.countslider.config(from_ = 2, to = 100)
        self.countslider.set(self.count)
        self.countslider.pack()

        self.svframe = Frame(master)
        self.svframe.pack()
        self.sslider = Scale(self.svframe, label="Saturation * 100",
                             length = 100,
                             orient=HORIZONTAL, command=self.sets)
        self.sslider.set(100)
        self.sslider.pack(side=LEFT)

        self.vslider = Scale(self.svframe, label="Value * 100",
                             length = 100,
                             orient=HORIZONTAL, command=self.setv)
        self.vslider.set(100)
        self.vslider.pack(side=LEFT)

    def init(self):
        self.keepgoing = True
        if self.sorteractive:
            self.sorter.quit()
        self.sorter = psort.Psort(self.count)
        self.sorteractive = True

    def run(self):
        if not self.sorteractive:
            self.init()
        self.keepgoing = True

        while self.keepgoing:
            lastorder = self.sorter.lastorder
            self.fromorderlabel.config(text=lastorder)
            method = self.sorter.choosemethod()
            self.methodlabel.config(text=method)
            order = self.sorter.chooseorder()
            self.toorderlabel.config(text=order)
            self.sorter.runsort(method=method, order=order, pause=1000)

        self.sorter.cyclemult = self.savecyclemult

    def stop(self):
        self.keepgoing = False
        self.savecyclemult = self.sorter.cyclemult
        self.sorter.cyclemult = 0

    def quit(self):
        self.stop()
        if self.sorteractive:
            self.sorter.quit()
        self.master.destroy()

    def setRate(self, v):
        val = self.rateslider.get()
        if self.sorteractive:
            self.sorter.cyclemult = 0.1**(val/10.0)

    def setCount(self, v):
        val = self.countslider.get()
        self.count = val
        self.init()

    def sets(self, v):
        if self.sorteractive:
            val = self.sslider.get()
            self.sorter.set_spectrum(s = val / 100.0)

    def setv(self, v):
        if self.sorteractive:
            val = self.vslider.get()
            self.sorter.set_spectrum(v = val / 100.0)

root = Tk()

gui = Gui(root)

root.mainloop()


