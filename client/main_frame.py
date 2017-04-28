import requests
from threading import Thread
import wx
from gui import MainFrame


class MainFrameView(MainFrame):
    def __init__(self, parent):
        super(MainFrameView, self).__init__(parent)
        self.CreateStatusBar()
        self._gw = {
            'ip': '', 'mac': '', 'hostname': ''
        }
        # Check tuxcut server
        if not self.is_server():
            self.show_dialog('error', 'TuxCut Server stopped', 'PLease start TuxCut server and rerun the appp')
            self.Close()
        else:
            # Get the gw
            self.get_gw()

            # setup host_view
            self.hosts_view.AppendIconTextColumn('', width=30)
            self.hosts_view.AppendTextColumn('IP Address', width=150)
            self.hosts_view.AppendTextColumn('MAC Address', width=150)
            self.hosts_view.AppendTextColumn('Hostname')
            self.trigger_thread()

    def trigger_thread(self):
        self.PushStatusText('Refreshing hosts list ...')
        t = Thread(target=self.t_get_hosts)
        t.start()

    def on_exit(self, event):
        print('Exit')
        self.Close()

    def on_refresh(self, event):
        self.trigger_thread()

    def t_get_hosts(self):
        res = requests.get('http://127.0.0.1:8013/scan/192.168.1.9')
        if res.status_code == 200:
            live_hosts = res.json()['result']['hosts']
            wx.CallAfter(self.fill_hosts_view, live_hosts)

    def fill_hosts_view(self, live_hosts):
        self.hosts_view.DeleteAllItems()
        for host in live_hosts:
            self.hosts_view.AppendItem([
                wx.dataview.DataViewIconText('', icon=wx.Icon('icons/online-24.png')),
                host['ip'],
                host['mac'],
                host['hostname']
            ])
        self.PushStatusText('Ready')

    def is_server(self):
        try:
            res = requests.get('http://127.0.0.1:8013/status')
            if res.status_code == 200 and res.json()['status'] == 'success':
                print('server running')
                return True
        except Exception as e:
            print('server stopped')
            return False

    def get_gw(self):
        try:
            res = requests.get('http://127.0.0.1:8013/gw')
            if res.status_code == 200 and res.json()['status'] == 'success':
                self._gw = res.json()['gw']
            elif res.status_code == 200 and res.json()['status'] == 'error':
                self.show_dialog('error', 'Error', res.json()['msg'])
                self.Close()
        except Exception as e:
            pass

    def show_dialog(self, code, title, msg):
        if code == 'error':
            icon = wx.ICON_ERROR
        dlg = wx.MessageDialog(None, msg, title, wx.OK | icon)
        dlg.ShowModal()
        dlg.Destroy()
