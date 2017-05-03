import sys
import logging
import subprocess as sp
import netifaces
import json
from scapy.all import *
from bottle import route, run, error
from bottle import request, response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = logging.FileHandler('/var/log/tuxcut/tuxcut-server.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)



def get_hostname(ip):
    """
    use nslookup from dnsutils package to get hostname for an ip
    """
    ans = sp.Popen(['nslookup', ip], stdout=sp.PIPE)
    for line in ans.stdout:
        line = line.decode('utf-8')
        if 'name = ' in line:
            return line.split(' ')[-1].strip('.\n')

def enable_ip_forward(self):
    sp.Popen(['sysctl', '-w', 'net.ipv4.ip_forward=1'])

def disable_ip_forward(self):
    sp.Popen(['sysctl', '-w', 'net.ipv4.ip_forward=0'])

def arp_spoof(self, victim_ip, victim_hw):
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

        send(pkt_1, count=3)
        send(pkt_2, count=3)

def arp_unspoof(self, victim_ip, victim_hw):
    # Correct  the victim arp table
    pkt_1 = ARP()
    pkt_1.op = 2
    pkt_1.psrc = self.gwip
    pkt_1.hwsrc = self.gwhw
    pkt_1.pdst = victim_ip
    pkt_1.hwdst = victim_hw

    # Correct  the gateway arptable
    pkt_2 = ARP()
    pkt_2.op = 2
    pkt_2.psrc = victim_ip
    pkt_2.hwsrc = victim_hw
    pkt_2.pdst = self.gwip
    pkt_2.hwdst = self.gwhw

    send(pkt_1, count=3)
    send(pkt_2, count=3)


@route('/status')
def get_ifaces():
    """
    check if server is running
    """
    response.headers['Content-Type'] = 'application/json'

    return json.dumps({
        'status':  'success',
        'msg': 'TuxCut server is running'
    })


# @route('/ifaces')
# def get_ifaces():
#     """
#     all the available network interfaces except  'lo'
#     """
#     response.headers['Content-Type'] = 'application/json'
#     ifaces = netifaces.interfaces()
#     if 'lo' in ifaces:
#         ifaces.remove('lo')
#     return json.dumps({
#         'status': 'success',
#         'ifaces': ifaces
#     })


@route('/my/<iface>')
def get_my(iface):
    """
    find the IP and MAC  addressess for the given interface
    """
    response.headers['Content-Type'] = 'application/json'
    get_addr = netifaces.ifaddresses(iface)

    if netifaces.AF_INET in get_addr:
        my_ip = get_addr[netifaces.AF_INET][0]['addr']
        my_mac = netifaces.ifaddresses(iface)[netifaces.AF_LINK][0]['addr']
    else:
        # iface not connected
        return json.dumps({
            'status': 'error',
            'msg': 'Network Card ({}) is not connected to any network'.format(iface)
        })

    return json.dumps({
        'status': 'success',
        'my': {
            'ip': my_ip,
            'mac': my_mac,
            'hostname': get_hostname(my_ip)
        }
    })


@route('/gw')
def get_default_gw():
    """
    Get the default gw ip address with the iface
    """
    response.headers['Content-Type'] = 'application/json'

    if netifaces.AF_INET in netifaces.gateways()['default']:
        default_gw = netifaces.gateways()['default'][netifaces.AF_INET]

        # initialize gw_mac with empty string
        gw_mac = ''

        # send arp packet to gw to get the MAC Address of the router
        results, unanswered = sr(ARP(op=ARP.who_has, psrc='8.8.8.8', pdst=default_gw[0]))
        for r in results[0]:
            if r.psrc == default_gw[0]:
                gw_mac = r.hwsrc

        return json.dumps({
            'status': 'success',
            'gw': {
                'ip': default_gw[0],
                'mac': gw_mac,
                'hostname': get_hostname(default_gw[0]),
                'iface': default_gw[1]
            }
        })
    else:
        print('No internet')
        return json.dumps({
            'status': 'error',
            'msg': 'This computer is not connected'
        })


@route('/scan/<gw_ip>')
def scan(gw_ip):
    response.headers['Content-Type'] = 'application/json'
    live_hosts = list()

    ans, unans = arping('{}/24'.format(gw_ip), verbose=False)

    for i in range(0, len(ans)):
        live_hosts.append ({
            'ip': ans[i][1].psrc,
            'mac': ans[i][1].hwsrc,
            'hostname': get_hostname(ans[i][1].psrc)
        })

    return json.dumps({
        'result': {
            'status': 'success',
            'hosts': live_hosts
        }
    })


@route('/protect', method='POST')
def enable_protection():
    response.headers['Content-Type'] = 'application/json'
    
    gw_ip = request.forms.get('ip')
    gw_mac = request.forms.get('mac')

    try:
        sp.Popen(['arptables', '-F'])
        sp.Popen(['arptables', '-P', 'INPUT', 'DROP'])
        sp.Popen(['arptables', '-P', 'OUTPUT', 'DROP'])
        sp.Popen(['arptables', '-A', 'INPUT', '-s', gw_ip, '--source-mac', gw_mac, '-j', 'ACCEPT'])
        sp.Popen(['arptables', '-A', 'OUTPUT', '-d', gw_ip, '--destination-mac', gw_mac, '-j', 'ACCEPT'])
        sp.Popen(['arp', '-s',  gw_ip, gw_mac ])
        return json.dumps({
            'status': 'success',
            'msg': 'Protection Enabled'
        })
    except Exception as e:
        logger.error(sys.exc_info()[1], exc_info=True)
        return json.dumps({
            'status': 'error',
            'msg': sys.exc_info()[1]
        })


@route('/unprotect')
def disable_protection():
    response.headers['Content-Type'] = 'application/json'
    try:
        sp.Popen(['arptables', '-P', 'INPUT', 'ACCEPT'])
        sp.Popen(['arptables', '-P', 'OUTPUT', 'ACCEPT'])
        sp.Popen(['arptables', '-F'])
        return json.dumps({
            'status': 'success',
            'msg': 'Protection Disabled'
        })
    except Exception as e:
        logger.error(sys.exc_info()[1], exc_info=True)
        return json.dumps({
            'status': 'error',
            'msg': sys.exc_info()[1]
        })
    



if __name__ == '__main__':
    run(host='127.0.0.1', port=8013, reloader=True)