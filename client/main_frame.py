import sys
import requests
from threading import Thread
import wx
from gui import MainFrame
import icons


class MainFrameView(MainFrame):
    def __init__(self, parent):
        super(MainFrameView, self).__init__(parent)
        self.CreateStatusBar()
        self.setup_toolbar()
        self.Centre()

        self.SetIcon(icons.ninja_32.GetIcon())

        self._gw = dict()
        self._my = dict()
        self.live_hosts = list()
        self._offline_hosts = list()

        # Check tuxcut server
        if not self.is_server():
            self.show_dialog('error', 'TuxCut Server stopped', 'Please start TuxCut server and rerun the appp')
            self.Close()
        else:
            # Get the gw
            self.get_gw()
            iface = self._gw['iface']
            self.get_my(iface)

            # setup host_view
            self.hosts_view.AppendIconTextColumn('', width=30)
            self.hosts_view.AppendTextColumn('IP Address', width=150)
            self.hosts_view.AppendTextColumn('MAC Address', width=150)
            self.hosts_view.AppendTextColumn('Hostname')

            self.trigger_thread()

    def setup_toolbar(self):
        tbtn_refresh = self.toolbar.AddTool(-1, '', icons.refresh_32.GetBitmap(), shortHelp='Refresh')
        tbtn_cut = self.toolbar.AddTool(-1, '', icons.cut_32.GetBitmap(), shortHelp='Cut')
        tbtn_resume = self.toolbar.AddTool(-1, '', icons.resume_32.GetBitmap(), shortHelp='Resume')

        self.toolbar.AddSeparator()
        tbtn_exit = self.toolbar.AddTool(-1, '', icons.exit_32.GetBitmap())

        self.Bind(wx.EVT_TOOL, self.on_refresh, tbtn_refresh)
        self.Bind(wx.EVT_TOOL, self.on_cut, tbtn_cut)
        self.Bind(wx.EVT_TOOL, self.on_resume, tbtn_resume)
        self.Bind(wx.EVT_TOOL, self.on_exit, tbtn_exit)

    def set_status(self, msg):
        self.PushStatusText(msg)

    def on_cut(self, event):

        row = self.hosts_view.GetSelectedRow()
        if not row == wx.NOT_FOUND:
            new_victim = {
                'ip': self.hosts_view.GetTextValue(row, 1),
                'mac': self.hosts_view.GetTextValue(row, 2),
                'hostname': self.hosts_view.GetTextValue(row, 3)
            }

            res = requests.post('http://127.0.0.1:8013/cut', json=new_victim)
            if res.status_code == 200 and res.json()['status'] == 'success':
                offline_icon = wx.dataview.DataViewIconText('', icon=icons.offline_24.GetIcon())
                self.hosts_view.SetValue(offline_icon, row, 0)
                self.set_status('{} is now offline'.format(new_victim['ip']))

                if new_victim['ip'] not in self._offline_hosts:
                    self._offline_hosts.append(new_victim['ip'])
        else:
            self.set_status('please select a victim to cut')

    def on_resume(self, event):
        self.set_status('Resuming host ...')
        t = Thread(target=self.t_resume)
        t.start()

    def trigger_thread(self):
        self.PushStatusText('Refreshing hosts list ...')
        t = Thread(target=self.t_get_hosts)
        t.start()

    def on_exit(self, event):
        print('Exit')
        self.unprotect()
        self.Close()

    def on_refresh(self, event):
        self.trigger_thread()

    def t_get_hosts(self):
        res = requests.get('http://127.0.0.1:8013/scan/{}'.format(self._my['ip']))
        if res.status_code == 200:
            self.live_hosts = res.json()['result']['hosts']
            wx.CallAfter(self.fill_hosts_view, self.live_hosts)

    def t_resume(self):
        row = self.hosts_view.GetSelectedRow()
        if not row == wx.NOT_FOUND:
            victim = {
                'ip': self.hosts_view.GetTextValue(row, 1),
                'mac': self.hosts_view.GetTextValue(row, 2),
                'hostname': self.hosts_view.GetTextValue(row, 3)
            }

            res = requests.post('http://127.0.0.1:8013/resume', json=victim)
            if res.status_code == 200 and res.json()['status'] == 'success':
                online_icon = wx.dataview.DataViewIconText('', icon=icons.online_24.GetIcon())
                self.hosts_view.SetValue(online_icon, row, 0)
                if victim['ip'] in self._offline_hosts:
                    self._offline_hosts.remove(victim['ip'])
                wx.CallAfter(self.set_status, '{} is back online'.format(victim['ip']))

    def fill_hosts_view(self, live_hosts):
        self.hosts_view.DeleteAllItems()
        for host in live_hosts:
            if host['ip'] not in self._offline_hosts:
                host_icon = wx.dataview.DataViewIconText('', icon=icons.online_24.GetIcon())
            else:
                host_icon = wx.dataview.DataViewIconText('', icon=icons.offline_24.GetIcon())
            self.hosts_view.AppendItem([
                host_icon,
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
                sys.exit()
        except Exception as e:
            pass

    def get_my(self, iface):
        try:
            res = requests.get('http://127.0.0.1:8013/my/{}'.format(iface))

            if res.status_code == 200 and res.json()['status'] == 'success':
                self._my = res.json()['my']

            elif res.status_code == 200 and res.json()['status'] == 'error':
                self.show_dialog('error', 'Error', res.json()['msg'])
                self.Close()
        except Exception as e:
            pass

    def toggle_protection(self, event):
        if self.cb_protection.GetValue():
            self.protect()
        else:
            self.unprotect()
            
    def protect(self):
        """
        Enable Protection Mode
        """
        try:
            res = requests.post('http://127.0.0.1:8013/protect', data=self._gw)
            if res.status_code == 200 and res.json()['status'] == 'success':
                self.PushStatusText('Protection Enabled')
        except Exception as e:
            print(sys.exc_info()[1])
    
    def unprotect(self):
        """
        Disable Protection Mode
        """
        try:
            res = requests.get('http://127.0.0.1:8013/unprotect')
            if res.status_code == 200 and res.json()['status'] == 'success':
                self.PushStatusText('Protection Disabled')
        except Exception as e:
            print(sys.exc_info()[1])

    def show_dialog(self, code, title, msg):
        if code == 'error':
            icon = wx.ICON_ERROR
        dlg = wx.MessageDialog(None, msg, title, wx.OK | icon)
        dlg.ShowModal()
        dlg.Destroy()
