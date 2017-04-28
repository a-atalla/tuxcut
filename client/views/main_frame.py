import requests
import wx
import wx.dataview
from ui import MainFrame


class MainFrameView(MainFrame):
    def __init__(self, parent):
        super(MainFrameView, self).__init__(parent)

        # setup host_view
        self.hosts_view.AppendIconTextColumn('', width=25)
        self.hosts_view.AppendTextColumn('IP Address', width=150)
        self.hosts_view.AppendTextColumn('MAC Address', width=150)
        self.hosts_view.AppendTextColumn('Hostname')
        self.get_live_hosts()

        refresh_tool = self.toolbar.AddTool(-1, '', wx.Bitmap('views/icons/refresh.png'))
        self.Bind(wx.EVT_TOOL, self.on_refresh, refresh_tool)

        exit_tool = self.toolbar.AddTool(-1, '', wx.Bitmap('views/icons/exit.png'))
        self.Bind(wx.EVT_TOOL, self.on_exit, exit_tool)

    def on_exit(self, event):
        print('Exit')
        self.Close()

    def on_refresh(self, event):
        self.get_live_hosts()

    def get_live_hosts(self):
        self.hosts_view.DeleteAllItems()
        res = requests.get('http://127.0.0.1:8013/scan/192.168.1.9')
        if res.status_code == 200:
            live_hosts = res.json()['result']['hosts']
            print (live_hosts)
            for host in live_hosts:
                self.hosts_view.AppendItem([
                    wx.dataview.DataViewIconText('', icon=wx.Icon('views/icons/online-16.png')),
                    host['ip'],
                    host['mac'],
                    host['hostname']
                ])

