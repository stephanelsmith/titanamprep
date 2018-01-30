
import os,sys,re
import time
import subprocess

from application import appwd

def wifi_get_wlans(verbose=False):
    internalmac = wifi_get_internalmac()
    wlans = []

    cmd = 'iwconfig'
    try:
        r = subprocess.check_output(cmd, shell=True).strip()
    except subprocess.CalledProcessError:
        raise
    if verbose:
        print r
    for line in r.split('\n'):
        m = re.match('^(?P<wlan>wlan\d+)', line, re.I)
        if m:
            wlan = m.group('wlan')
            mac = wifi_get_mac(wlan)
            if mac == None:
                break
            isinternal = False
            if internalmac == mac:
                isinternal = True
            wlans.append({'wlan':wlan,'mac':mac, 'isinternal':isinternal})
    print wlans
    return wlans

def wifi_get_internalmac():
    internalmacfile = appwd+'/'+'static/internalmac.txt'
    with open(internalmacfile) as f:
        return f.read().strip()

def wifi_get_mac(wlan):
    cmd = 'ifconfig '+wlan
    try:
        r = subprocess.check_output(cmd, shell=True).strip()
    except subprocess.CalledProcessError:
        return None
    for line in r.split('\n'):
        m = re.match('\s*ether\s+(?P<mac>[\d\w\:]+)', line, re.I)
        if m:
            return m.group('mac')
        m = re.search('\s*HWaddr\s+(?P<mac>[\d\w\:]+)', line, re.I)
        if m:
            return m.group('mac')
    return None
    


def wifi_isconnected(wlan):
    cmd = 'wpa_cli -i '+wlan+' status'
    try:
        r = subprocess.check_output(cmd, shell=True).strip()
    except subprocess.CalledProcessError:
        raise
    wpa_state = None
    for line in r.split('\n'):
        m = re.match('wpa_state=(?P<wpa_state>\w+)', line, re.I)
        if m:
            wpa_state = m.group('wpa_state')
    if wpa_state == 'COMPLETED':
        return True
    return False

def wifi_ssid(wlan):
    cmd = 'wpa_cli -i '+wlan+' list_networks'
    try:
        r = subprocess.check_output(cmd, shell=True).strip()
    except subprocess.CalledProcessError:
        raise
    ssid = None
    for line in r.split('\n'):
        m = re.match('(?P<id>\d+)\s+(?P<ssid>[\[\]\w\-\_]+)\s+\w+\s+\[current\]', line, re.I)
        if m:
            ssid = m.group('ssid')
    return ssid

def wifi_connect(wlan, ssid, password, verbose=False):
    cmd = 'wpa_cli -i '+wlan+' remove_network all'
    if verbose:
        print cmd
    try:
        r = subprocess.check_output(cmd, shell=True).strip()
    except subprocess.CalledProcessError:
        raise
    if verbose:
        print r
    if r != 'OK':
        raise Exception(r)
    cmd = 'wpa_cli -i '+wlan+' add_network 0'
    if verbose:
        print cmd
    try:
        r = subprocess.check_output(cmd, shell=True).strip()
    except subprocess.CalledProcessError:
        raise
    if verbose:
        print r
    if r != '0':
        raise Exception(r)
    cmd = 'wpa_cli -i '+wlan+' set_network 0 ssid \'"'+ssid+'"\''
    if verbose:
        print cmd
    try:
        r = subprocess.check_output(cmd, shell=True).strip()
    except subprocess.CalledProcessError:
        raise
    if verbose:
        print r
    if r != 'OK':
        raise Exception(r)
    cmd = 'wpa_cli -i '+wlan+' set_network 0 psk \'"'+password+'"\''
    if verbose:
        print cmd
    try:
        r = subprocess.check_output(cmd, shell=True).strip()
    except subprocess.CalledProcessError:
        raise
    if verbose:
        print r
    if r != 'OK':
        raise Exception(r)
    cmd = 'wpa_cli -i '+wlan+' enable_network 0'
    if verbose:
        print cmd
    try:
        r = subprocess.check_output(cmd, shell=True).strip()
    except subprocess.CalledProcessError:
        raise
    if verbose:
        print r
    if r != 'OK':
        raise Exception(r)

def wifi_connect_connectwait(wlan):
    loop = 10
    while loop>0:
        cmd = 'wpa_cli -i '+wlan+' status'
        try:
            r = subprocess.check_output(cmd, shell=True).strip()
        except subprocess.CalledProcessError:
            raise
        wpa_state = None
        for line in r.split('\n'):
            m = re.match('wpa_state=(?P<wpa_state>\w+)', line, re.I)
            if m:
                wpa_state = m.group('wpa_state')
        print wpa_state
        if wpa_state == 'INACTIVE' or wpa_state == 'DISCONNECTED':
            return False
        if wpa_state == 'CONNECTED' or wpa_state == 'COMPLETED':
            return True
        time.sleep(1)
        loop -= 1
    return False

def wifi_connect_ipwait(wlan):
    loop = 30
    while wifi_get_ip(wlan)==None and loop>0:
        time.sleep(1)
        loop -= 1
    if wifi_get_ip(wlan)!=None:
        return True
    return False

def wifi_get_ip(wlan):
    cmd = 'wpa_cli -i '+wlan+' status'
    try:
        r = subprocess.check_output(cmd, shell=True).strip()
    except subprocess.CalledProcessError:
        raise
    ip_address = None
    for line in r.split('\n'):
        m = re.match('ip_address=(?P<ip_address>[\d\.]+)', line, re.I)
        if m:
            ip_address = m.group('ip_address')
    return ip_address

def wifi_disconnect(wlan):
    cmd = 'wpa_cli -i '+wlan+' disable_network 0'
    try:
        r = subprocess.check_output(cmd, shell=True).strip()
    except subprocess.CalledProcessError:
        raise
    if r != 'OK':
        raise Exception(r)

def wifi_scan(wlan, verbose=False):
    cmd = 'wpa_cli -i '+wlan+' scan'
    if verbose:
        print cmd
    try:
        r = subprocess.check_output(cmd, shell=True).strip()
    except subprocess.CalledProcessError:
        raise
    if verbose:
        print r
    if r != 'OK':
        raise Exception(r)
    cmd = 'wpa_cli -i '+wlan+' scan_results'
    if verbose:
        print cmd
    try:
        r = subprocess.check_output(cmd, shell=True).strip()
    except subprocess.CalledProcessError:
        raise
    if verbose:
        print r
    apis = []
    for line in r.split('\n'):
        print line
        m = re.match('(?P<bssid>[\w\:]+)\s+(?P<frequency>\d+)\s+(?P<rssi>[-\d]+)\s+(?P<flags>[\[\]\w\-]+)\s+(?P<ssid>[\[\]\w\-\_]+)', line, re.I)
        if m:
            d = {}
            d['ssid'] = m.group('ssid')
            d['rssi'] = m.group('rssi')
            apis.append(d)
    apis = sorted(apis, key=lambda x:x['rssi'])
    return apis

    

