import requests,json,subprocess,time

def main():
   activate_defender(devInfoGrabber())


def isConnectionSuccess():
    counter = 0
    while counter != 5:
        time.sleep(1) 
        try:
           res = requests.get('http://127.0.0.1:8013/status')
           if res.status_code == 200:
              return True
        except requests.exceptions.ConnectionError:
              counter += 1
              print('The server seems to be preparing itself, retrying.....'+str(counter))
    return False


def devInfoGrabber():
    if isConnectionSuccess():
       res = requests.get('http://127.0.0.1:8013/gw')
       if res.status_code == 200 and res.json()['status'] == 'success':
            return res.json()['gw']
       elif res.status_code == 200 and res.json()['status'] == 'error':
            subprocess.run(["/usr/bin/zenity", "--error", "--text", "Cant connect to the tuxcut server even though the server was already running. Please make sure your internet interface was active"])
            exit()
    else:
       subprocess.run(["/usr/bin/zenity", "--error", "--text", "Tuxcut daemon server is not running, Please enable it first!"])
       exit()


def activate_defender(hwinfo):
    iface = hwinfo['iface']
    try:
       res = requests.post('http://127.0.0.1:8013/protect', data=hwinfo)
       if res.status_code == 200 and res.json()['status'] == 'success':
        requests.get('http://127.0.0.1:8013/change-mac/'+iface)
        subprocess.run(["/usr/bin/zenity", "--info", "--text", "Your PC is now protected from ARP spoofing attack!"])
        
    except:
        subprocess.run(["/usr/bin/zenity", "--error", "--text", "Failed to toggle protection. Please check your tuxcut daemon configuration"])


if __name__ == "__main__":
    main()




