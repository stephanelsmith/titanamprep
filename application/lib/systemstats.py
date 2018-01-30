
import os,sys,re

def get_serial():
    cmd = "cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2"
    return os.popen(cmd).read().strip()


def get_systemstats():
    memtot = 0
    memused = 0
    memfree = 0
    swaptot = 0
    swapused = 0
    swapfree = 0
    cmd = 'free'
    free = os.popen(cmd).read().strip()
    m = re.search('mem:\s+(?P<tot>\d+)\s+(?P<used>\d+)\s+(?P<free>\d+)', free, re.IGNORECASE)
    memtot = int(m.group('tot'))
    memused = int(m.group('used'))
    memfree = int(m.group('free'))
    m = re.search('swap:\s+(?P<tot>\d+)\s+(?P<used>\d+)\s+(?P<free>\d+)', free, re.IGNORECASE)
    swaptot = int(m.group('tot'))
    swapused = int(m.group('used'))
    swapfree = int(m.group('free'))

    return {'memtot':memtot,
            'memused':memused,
            'memfree':memfree,
            'swaptot':swaptot,
            'swapused':swapused,
            'swapfree':swapfree}

