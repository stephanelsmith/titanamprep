#!/usr/bin/tcsh
cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2
