import requests
from threading import Thread
import wx
from gui import MainFrame


class MainFrameView(MainFrame):
    def __init__(self, parent):
        super(MainFrameView, self).__init__(parent)
        self.CreateStatusBar()

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
            for host in live_hosts:
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