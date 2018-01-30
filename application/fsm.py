
import os,sys,re,time
import traceback

from simplejson import dumps as jsondumps
from simplejson import loads as jsonloads

from application.fsmbase import State
from application.fsmbase import FsmBase
from application.lib.retry import retryfunc

from application import devmode
from application import appwd

from application.lib.wifi import wifi_get_wlans
from application.lib.wifi import wifi_scan
from application.lib.wifi import wifi_ssid
from application.lib.wifi import wifi_connect
from application.lib.wifi import wifi_disconnect
from application.lib.wifi import wifi_isconnected
from application.lib.wifi import wifi_connect_connectwait
from application.lib.wifi import wifi_get_ip
from application.lib.wifi import wifi_connect_ipwait

from application.lib.hostservice import network_killall
from application.lib.hostservice import wpasupplicant_start
from application.lib.hostservice import wpasupplicant_stop

from application.lib.hostservice import hostapd_stop
from application.lib.hostservice import hostapd_writeconf
from application.lib.hostservice import hostapd_start
from application.lib.hostservice import hostapd_isrunning

from application.lib.hostservice import dnsmasq_stop
from application.lib.hostservice import dnsmasq_start
from application.lib.hostservice import dnsmasq_isrunning
from application.lib.hostservice import dnsmasq_writeconf

from application.lib.hostservice import dhcpcd_stop
from application.lib.hostservice import dhcpcd_start
from application.lib.hostservice import dhcpcd_release
from application.lib.hostservice import dhcpcd_allow
from application.lib.hostservice import dhcpcd_isrunning
from application.lib.hostservice import dhcpcd_writeconf
from application.lib.hostservice import dhcpcd_revertconf

from application.lib.hostservice import iptables_conf

from application.lib.hostservice import hostservice_connect_ipwait
from application.lib.hostservice import hostservice_get_stas
from application.lib.hostservice import hostservice_get_ip
from application.lib.hostservice import hostservice_get_ssid


from application import oled


class Fsm(FsmBase):
    def __init__(self):
        self.fsmdic = {}

        #fsm states
        self.fsm = {}
        self.fsm['start']         = State(name='start',
                                         func=self._start,
                                         nxtstateedges = {'next':'init'},
                                         description='')
        self.fsm['init']         = State(name='init',
                                         func=self._init,
                                         nxtstateedges = {'next':'reset'},
                                         description='')
        self.fsm['reset']         = State(name='reset',
                                         func=self._reset,
                                         nxtstateedges = {'next':'idwlandevices'},
                                         description='')
        self.fsm['idwlandevices']  = State(name='idwlandevices',
                                         func=self._idwlandevices,
                                         nxtstateedges = {'next':'wifiskip'},
                                         description='')
        self.fsm['wifiskip']  = State(name='wifiskip',
                                         func=self._wifiskip,
                                         nxtstateedges = {'next':'startdhcpcd',
                                                          'alreadyconnectedtowifi':'wificonnected'},
                                         description='')
        self.fsm['startdhcpcd']         = State(name='startdhcpcd',
                                         func=self._startdhcpcd,
                                         nxtstateedges = {'next':'wifiscan'},
                                         description='')
        self.fsm['wifiscan']         = State(name='wifiscan',
                                         func=self._wifiscan,
                                         nxtstateedges = {'next':'wificonnected'},
                                         description='')
        self.fsm['wificonnected']         = State(name='wificonnected',
                                         func=self._wificonnected,
                                         nxtstateedges = {'next':'starthostapd'},
                                         description='')
        self.fsm['starthostapd']         = State(name='starthostapd',
                                         func=self._starthostapd,
                                         nxtstateedges = {'next':'startdnsmasq'},
                                         description='')
        self.fsm['startdnsmasq']         = State(name='startdnsmasq',
                                         func=self._startdnsmasq,
                                         nxtstateedges = {'next':'serviceconnected'},
                                         description='')
        self.fsm['serviceconnected']         = State(name='serviceconnected',
                                         func=self._serviceconnected,
                                         nxtstateedges = {'next':'idle'},
                                         description='')
        self.fsm['idle']         = State(name='idle',
                                         func=self._idle,
                                         nxtstateedges = {'next':'exit'},
                                         description='')

        self.fsm['error']         = State(name='error',
                                         func=self._error,
                                         nxtstateedges = {'next':'start'},
                                         description='')

        self.fsm['exit']           = None

        #fsm start
        self.fsmstart = 'start'

        self.fsmdic = {}
        self.fsmdic['errorcount'] = 0

    def run(self):

        nxtstate = self.fsmstart


        while self.fsm[nxtstate]:
            try:
                #run state
                print self.fsm[nxtstate].name
                edge = self.fsm[nxtstate].func()

                #next state
                if edge in self.fsm[nxtstate].nxtstateedges.keys():
                    nxtstate = self.fsm[nxtstate].nxtstateedges[edge]
                elif edge in self.fsm.keys():
                    nxtstate = edge
                else:
                    raise Exception('Fsm edge error: ' + nxtstate + ' -> ' + edge +
                                    ' -> ' +  self.fsm[nxtstate].nxtstateedges[edge])
                    break
            except SystemExit:
                raise
            except Exception, err:
                print traceback.format_exc()
                nxtstate = 'error'
                time.sleep(1)

    def info(self, msg):
        print msg
    def warn(self, msg):
        print msg
    def error(self, msg):
        print msg

    def _start(self):
        print '==== START ===='
        return 'next'

    def _init(self):

        from application.lib.systemstats import get_serial
        self.fsmdic['deviceserial'] = get_serial()

        wifiapsfile = appwd+'/'+'wifiaps.json'
        try:
            self.fsmdic['wifiaps'] = jsonloads(open(wifiapsfile, 'r').read())
        except:
            self.fsmdic['wifiaps'] = []

        if devmode:
            self.fsmdic['wifiaps'].append({'ssid':'ThunderFace2',
                                           'password':'sararocksmyworld'})
            self.fsmdic['wifiaps'].append({'ssid':'DonCarnage',
                                           'password':'sararocksmyworld'})

	#with open(filename, 'w') as f:
	    #json = jsondumps(twitterleads2, separators=(',', ':'), use_decimal=True, sort_keys=True, indent=4)
	    #f.write(json)

        return 'next'


    def _reset(self):
        return 'next'


    def _idwlandevices(self):
        wlans =  wifi_get_wlans(verbose=True)
        for wlan in wlans:
            print wlan

        if len(wlans) < 2:
            print 'Not enough wlans'
            oled.setline(linenum=0,
                         msg='Please plug antenna',
                         clearlower=True)
            oled.draw()
            time.sleep(1)
            return 'idwlandevices'

        wifiwlan = None
        hostwlan = None

        internals = filter(lambda x:x['isinternal'], wlans)
        externals = filter(lambda x:not x['isinternal'], wlans)
        if len(externals) >= 2:
            wifiwlan = externals[0]
            hostwlan = externals[1]
        else:
            wifiwlan = internals[0]
            hostwlan = externals[0]

        if not wifiwlan or not hostwlan:
            print internals
            print externals
            print wifiwlan
            print hostwlan
            raise Exception('wifiwlan and hostwlan not configured')

        print 'wifiwlan: '+str(wifiwlan)
        print 'hostwlan: '+str(hostwlan)

        self.fsmdic['wifiwlan'] = wifiwlan['wlan']
        self.fsmdic['hostwlan'] = hostwlan['wlan']

        #write configuration files
        print 'writing /etc/dhcpcd.conf'
        dhcpcd_writeconf(wlan=self.fsmdic['hostwlan'])
        print 'writing /etc/hostapd/hostapd.conf'
        hostapd_writeconf(wlan=self.fsmdic['hostwlan'],
                          channel=6)
        print 'writing /etc/dnsmasq.conf'
        dnsmasq_writeconf(wlan=self.fsmdic['hostwlan'])
        print 'writing iptables'
        iptables_conf(wifiwlan=self.fsmdic['wifiwlan'],
                      hostwlan=self.fsmdic['hostwlan'],
                      verbose=True)

        print 'start wpasupplicant on wifiwlan'
        wpasupplicant_start(wlan=self.fsmdic['wifiwlan'])
        print 'terminate wpasupplicant on hostwlan'
        wpasupplicant_stop(wlan=self.fsmdic['hostwlan'])
        
        return 'next'

    def _wifiskip(self):
        try:
            if wifi_isconnected(wlan=self.fsmdic['wifiwlan']):
                return 'alreadyconnectedtowifi'
        except:
            pass
        return 'next'

    def _startdhcpcd(self):
        #print 'starting dhcpcd'
        oled.setline(linenum=2,
                     msg='Starting DHCPCD...',
                     clearlower=True)
        oled.draw()

        print 'release dhcpcd'
        dhcpcd_release(wlan=self.fsmdic['wifiwlan'])
        dhcpcd_release(wlan=self.fsmdic['hostwlan'])
        print 'allow dhcpcd'
        dhcpcd_allow(wlan=self.fsmdic['wifiwlan'])
        dhcpcd_allow(wlan=self.fsmdic['hostwlan'])
        #print 'revert dhcpcd'
        #dhcpcd_revertconf()

        #if dhcpcd_isrunning(verbose=True):
        #    print 'dhcpcd started'
        #else:
        #    raise Exception('dhcpcd failed to start')

        oled.setline(linenum=2,
                     msg='DHCPCD Started',
                     clearlower=True)
        oled.draw()

        return 'next'


    def _wifiscan(self):

        if wifi_isconnected(wlan=self.fsmdic['wifiwlan']):
            return 'next'

        print 'not connected, scanning...'
        oled.setline(linenum=0,
                     msg='Scanning...')
        oled.draw()

        aps = retryfunc(func=wifi_scan, 
                        args=[], kwargs={'wlan':self.fsmdic['wifiwlan'],
                                         'verbose':False}, 
                        retries=3,
                        delay=3,
                        fnwarn=self._wrapwarn)

        for ap in aps:
            print 'trying:'+str(ap)
            for kap in self.fsmdic['wifiaps']:
                print kap
                if kap['ssid'] == ap['ssid']:
                    print 'connecting to '+str(ap)
                    wifi_connect(wlan=self.fsmdic['wifiwlan'],
                                 ssid=kap['ssid'],
                                 password=kap['password'],
                                 verbose=True)

                    oled.setline(linenum=0,
                                msg='Connecting to...')
                    oled.setline(linenum=1,
                                msg=kap['ssid'],
                                clearlower=True)
                    oled.draw()

                    print 'waiting...'
                    r = wifi_connect_connectwait(wlan=self.fsmdic['wifiwlan'])
                    if not r:
                        print 'did not connect.'
                        oled.setline(linenum=0,
                                    msg='Did not connect')
                        oled.draw()
                        continue

                    print 'getting ip...'
                    ssid = str(wifi_ssid(wlan=self.fsmdic['wifiwlan']))
                    oled.setline(linenum=0,
                                msg='SSID:'+ssid)
                    oled.setline(linenum=1,
                                msg='Getting IP...',
                                clearlower=True)
                    oled.draw()

                    r = wifi_connect_ipwait(wlan=self.fsmdic['wifiwlan'])

                    if not r:
                        print 'did not get ip.'

                        oled.setline(linenum=0,
                                    msg='SSID:'+ssid)
                        oled.setline(linenum=1,
                                    msg='Did not get IP...',
                                    clearlower=True)
                        oled.draw()
                        time.sleep(1)

                        continue
                    #connected!
                    return 'next'
                else:
                    print ap

        print 'no networks found'
        oled.setline(linenum=0,
                    msg='No networks found...',
                    clearlower=True)
        oled.draw()
        time.sleep(4)
        return 'wifiscan'

    def _wificonnected(self):

        ssid = str(wifi_ssid(wlan=self.fsmdic['wifiwlan']))
        print 'connected to ssid: '+ssid
        ip = str(wifi_get_ip(wlan=self.fsmdic['wifiwlan']))
        print 'ip:'+ip
        oled.setline(linenum=0,
                     msg='SSID:'+ssid)
        oled.setline(linenum=1,
                     msg='IP:'+ip,
                     clearlower=True)
        oled.draw()
        return 'next'


    def _starthostapd(self):
        print 'dnsmasq stop'
        dnsmasq_stop()
        print 'hostapd stop'
        hostapd_stop()

        dhcpcd_release(wlan=self.fsmdic['hostwlan'])
        dhcpcd_allow(wlan=self.fsmdic['hostwlan'])

       
        print 'starting hostapd'
        oled.setline(linenum=2,
                     msg='Starting Host...',
                     clearlower=True)
        oled.draw()

        hostapd_start(wlan=self.fsmdic['hostwlan'],
                      retries=5,
                      verbose=True)
        if hostapd_isrunning(verbose=True):
            print 'hostapd started'
        else:
            raise Exception('hostapd failed to start')

        oled.setline(linenum=2,
                     msg='Host Started',
                     clearlower=True)
        oled.draw()

        return 'next'


    def _startdnsmasq(self):


        print 'starting dnsmasq'
        oled.setline(linenum=2,
                     msg='Starting DNS...',
                     clearlower=True)
        oled.draw()

        print 'wait before dnsmasq start...'
        time.sleep(14)


        dnsmasq_start(retries=5)
        if dnsmasq_isrunning(verbose=True):
            print 'dnsmasq started'
        else:
            raise Exception('dnsmasq failed to start')

        oled.setline(linenum=2,
                     msg='DNS Started',
                     clearlower=True)
        oled.draw()


        return 'next'

    def _serviceconnected(self):
        print 'getting hostservice ip'
        hostservice_connect_ipwait(wlan=self.fsmdic['hostwlan'], verbose=True)
        hostservice_ip = hostservice_get_ip(wlan=self.fsmdic['hostwlan'], verbose=True)
        hostservice_ssid =  hostservice_get_ssid(wlan=self.fsmdic['hostwlan'])
        if hostservice_ip == None:
            raise Exception('no host service ip')
        print 'hostservice ip:'+str(hostservice_ip)
        print 'hostservice ssid:'+str(hostservice_ssid)

        oled.setline(linenum=2,
                     msg='BSSID:'+str(hostservice_ssid),
                     clearlower=True)
        oled.draw()
        return 'next'

    def _idle(self):
        wlans =  wifi_get_wlans(verbose=True)
        if len(wlans)<2:
            print 'Not enough wlans'
            return 'error'

        stas = hostservice_get_stas(wlan=self.fsmdic['hostwlan'])
        nstats = len(stas)
        print 'connected devices:'+str(nstats)
        oled.setline(linenum=3,
                     msg='Devices:'+str(nstats),
                     clearlower=True)
        oled.draw()
        time.sleep(1)
        return 'idle'

    def _error(self):
        self.fsmdic['errorcount'] = self.fsmdic['errorcount'] + 1
        if self.fsmdic['errorcount'] > 3:
            print 'REBOOTING'
            time.sleep(1)
            os.system('reboot')
        print 'Kill all interfaces'
        #network_killall(verbose=True)
        dhcpcd_stop()
        dnsmasq_stop()
        hostapd_stop()
        return 'next'

