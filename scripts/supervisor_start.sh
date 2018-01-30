#!/usr/bin/tcsh

ps auxww | grep 'titanamp' | grep -v 'supervisor' | awk '{print $2}' | xargs kill -9

gpio mode 29 in
gpio mode 29 up
setenv ISPRODUCTION `gpio read 29`
echo $ISPRODUCTION
if ($ISPRODUCTION == 1) then
    echo "PRODUCTION MODE"
    setenv DIR "/root/titanamprep"
else
    echo "DEV MODE"
    setenv DIR "/root/titanamp"
endif

cd $DIR
$DIR/env/bin/python $DIR/run.py 

