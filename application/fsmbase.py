

import os,sys,re,time
import traceback

class State:
    def __init__(self, name='null', func=None, nxtstateedges={},description=None, quiet=False):
        self.func = func
        self.nxtstateedges = nxtstateedges
        self.name = name
        self.description = description
        self.quiet = quiet



class FsmBase(object):
    def __init__(self):
	pass

    def _wrapwarn(self):
        print traceback.format_exc()




