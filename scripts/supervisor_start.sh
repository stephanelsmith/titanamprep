#!/usr/bin/tcsh

ps auxww | grep 'titanamp' | grep -v 'supervisor' | awk '{print $2}' | xargs kill -9
setenv DIR "/root/titanamp"
$DIR/env/bin/python $DIR/run.py 
