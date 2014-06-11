##################################################################
## Xiaofan Li
## Pausch Bridge Sorting Debug Script
## Summer 2014
## Turns everything to a desired color -- python
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
    color = raw_input("Enter color red/blue/green: ")
    interval = input ("Interval (sec): ")
    
    ## error checking
    while color!='red' and color!='green' and color!='blue':
        print "invalid color need red/green/blue"
        color = raw_input ("Enter color again: ")
    
    while interval<0 or interval>60:
        print "invalid interval need:[0,60)"
        interval = input ("Interval: (sec) ")

      

    ## turn on one by one
    for x in range (0, num_lights) : 
        lights.getChannel(x).setParam(color,1.0)
        time.sleep(interval)


