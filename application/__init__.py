
import sys, os, re, traceback
import subprocess

__version__ = '1.1.2'




appwd = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))

cmd = appwd+'/scripts/get_serial.sh'
serial = subprocess.check_output(cmd, shell=True).strip()
print 'SERIAL:'+str(serial)

cmd = appwd+'/scripts/get_isproduction.sh'
devmode = not bool(int(subprocess.check_output(cmd, shell=True).strip()))
print 'DEVMODE:'+str(devmode)

from application.lib.oled import OLED
oled = OLED()

from application.fsm import Fsm
fsm = Fsm()



