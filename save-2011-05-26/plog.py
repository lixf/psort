#!/usr/bin/python

# Run sort to log step counts
import psort

p = psort.Psort(n = 360, nodisplay = True)

p.run(s = 200000, log = True, time = 1)


