##################################################################
## Xiaofan Li
## Pausch Bridge Sorting Debug Script
## Summer 2014
## Make a white panel go thru the bridge to test
## actual response performance -- python
#################################################################

## set up
import lumiversepython as l
import os
import time

## just get json path as environment var
json = os.environ.get('JSON')
if json == 'None':
    print "Cannot see JSON file, going to use default"

lights = l.Rig(json)
lights.init()
lights.run()

## number of channels on the bridge
num_lights = 57

## rate is frames/sec or packets sent/sec
rate = 60

while True : 
    ## ask for rate
    rate = input ("rate of change (frames/sec) : ")
    
    ## error checking
    while rate<0 or rate>60:
        print "rate out of range: [0,60)"
        interval = input ("Interval: (sec) ")

    ## turn on one by one and keeps looping
    prev = 0
    interval = 1.0/(float(rate))
    while True :
        for x in range (0, num_lights) : 
            lights.getChannel(x).setParam("red",1.0)
            lights.getChannel(x).setParam("green",1.0)
            lights.getChannel(x).setParam("blue",1.0)
            
            ## turn off the previous one
            lights.getChannel(prev).setParam("red",0.0)
            lights.getChannel(prev).setParam("green",0.0)
            lights.getChannel(prev).setParam("blue",0.0)
            
            prev = x
            # this does take floats
            time.sleep(interval)


