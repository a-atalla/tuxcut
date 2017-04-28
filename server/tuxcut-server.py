import sys
import subprocess as sp
import netifaces
import json
from scapy.all import *
from bottle import route, run, error
from bottle import request, response


def get_hostname(ip):
    """
    use nslookup from dnsutils package to get hostname for an ip
    """
    ans = sp.Popen(['nslookup', ip], stdout=sp.PIPE)
    for line in ans.stdout:
        line = line.decode('utf-8')
        if 'name = ' in line:
            return line.split(' ')[-1].strip('.\n')


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
        'result': {
            'status': 'success',
            'my': {
                'ip': my_ip,
                'mac': my_mac,
                'hostname': get_hostname(my_ip)
            }
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
    print(ans.summary())

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




if __name__ == '__main__':
    run(host='127.0.0.1', port=8013, reloader=True)