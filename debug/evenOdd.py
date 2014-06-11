##################################################################
## Xiaofan Li
## Pausch Bridge Sorting Debug Script
## Summer 2014
## turns on/off even odd lights (very annoyingly) -- python
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

while True : 
    ## ask for color to turn the bridge
    color = raw_input ("Enter color red/blue/green: ")
    interval = input ("Interval (sec): ")
    times = input ("How many times? ")
    
    ## error checking
    while color!='red' and color!='green' and color!='blue':
        print "invalid color need red/green/blue"
        color = raw_input ("Enter color again: ")
    
    while interval<0 or interval>60:
        print "invalid interval need:[0,60)"
        interval = input ("Interval: (sec) ")

    while times<0 :
        print "invalid interval need:[0,inf)"
        interval = input ("How many times? ")
    
    while times > 0 : 
        times = times-1;
        odd = True
        ## turn on one by one based on odd/even-ness
        for x in range (0, num_lights) : 
            isOdd = (x%2 != 0)
            on = (odd & isOdd) | (~odd & ~isOdd)
            if on:
                lights.getChannel(x).setParam(color,1.0)
            else:
                lights.getChannel(x).setParam(color,0.0)

        time.sleep(interval)


