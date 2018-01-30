
import os,sys,re


import sys, os, re, traceback

__version__ = '1.1.2'


devmode = True

#from application.lib.getserial import get_serial
#deviceserial = get_serial()

appwd = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))

from application.lib.oled import OLED
oled = OLED()

from application.fsm import Fsm
fsm = Fsm()



