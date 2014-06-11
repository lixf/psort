########################################################################
## Xiaofan Li                                                       
## Pausch Bridge Debugging Script
## Summer 2014
#######################################################################

## This script initializes the environment variables and calls 
## the desired python scripts
##

## Edit on different machine
## Points to executables
LUMIVERSE_PATH='/home/xiaofan/Work/research/Lumiverse/Lumiverse/build/LumiverseCore'
PSORT_PATH='/home/xiaofan/Work/research/pysort/psort/bridge'
## support different json files
JSONFILE='PauschBridge.json'

## set environment variable
echo "setting child process env vars: PYTHONPATH="
export PYTHONPATH=$LUMIVERSE_PATH:$PSORT_PATH
echo $PYTHONPATH
echo "JSON="
export JSON=$LUMIVERSE_PATH/$JSONFILE
echo $JSON

## excute python
while true; do
  read -p "which python script to run? " CHOICE
  case $CHOICE in
    oneColor ) python oneColor.py ; echo "oneColor Done";;
    goThru   ) python goThru.py ; echo "goThru Done";;
    graphic  ) python $PSORT_PATH/bridge.py ; exit;;
    sort     ) python $PSORT_PATH/bridge.py -r $JSON   ; exit;;
    exit     ) exit;;
    * ) echo "options: allWhite/goThru/graphic/sort";;
  esac
done
