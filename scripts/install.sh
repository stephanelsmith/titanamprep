#!/usr/bin/tcsh

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

echo "cp $DIR/scripts/supervisor_start.sh /root/supervisor_start.sh"
cp $DIR/scripts/supervisor_start.sh /root/supervisor_start.sh

echo "cp $DIR/scripts/supervisor_titanamp.conf /etc/supervisor/conf.d/titanamp.conf"
cp $DIR/scripts/supervisor_titanamp.conf /etc/supervisor/conf.d/titanamp.conf

echo "cp $DIR/scripts/ib_oled_splash /etc/init.d/ib_oled_splash"
cp $DIR/scripts/ib_oled_splash /etc/init.d/ib_oled_splash

echo "cp $DIR/scripts/ib_cleanup /etc/init.d/ib_cleanup"
cp $DIR/scripts/ib_cleanup /etc/init.d/ib_cleanup




