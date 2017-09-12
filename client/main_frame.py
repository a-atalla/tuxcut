import os
import sys
import logging
from pathlib import Path
import shelve
import requests
from threading import Thread
import wx
from gui import MainFrame
import icons

APP_DIR = os.path.join(str(Path.home()), '.tuxcut')
if not os.path.isdir(APP_DIR):
    os.mkdir(APP_DIR)
    client_log = Path(os.path.join(APP_DIR, 'tuxcut.log'))
    client_log.touch(exist_ok=True)
    client_log.chmod(0o666)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('tuxcut-client')
handler = logging.FileHandler(os.path.join(APP_DIR, 'tuxcut.log'))
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class MainFrameView(MainFrame):
    def __init__(self, parent):
        super(MainFrameView, self).__init__(parent)
        self.CreateStatusBar()
        self.setup_toolbar()
        self.Centre()

        self.SetIcon(icons.ninja_32.GetIcon())

        self.aliases = shelve.open( os.path.join(APP_DIR, 'aliases.db'))
        # initialize
        self._gw = dict()
        self._my = dict()
        self.live_hosts = list()
        self._offline_hosts = list()

        # Check tuxcut server
        if not self.is_server():
            self.show_dialog('error',
                             'TuxCut Server stopped',
                             "use 'systemctl start tuxcut-server' then restart the application")
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
            self.hosts_view.AppendTextColumn('Hostname', width=200)
            self.hosts_view.AppendTextColumn('Alias')

            self.trigger_thread()


    def setup_toolbar(self):
        tbtn_refresh = self.toolbar.AddTool(-1, '', icons.refresh_32.GetBitmap(), shortHelp='Refresh')
        tbtn_cut = self.toolbar.AddTool(-1, '', icons.cut_32.GetBitmap(), shortHelp='Cut')
        tbtn_resume = self.toolbar.AddTool(-1, '', icons.resume_32.GetBitmap(), shortHelp='Resume')
        self.toolbar.AddSeparator()
        tbtn_change_mac = self.toolbar.AddTool(-1, '', icons.mac_32.GetBitmap(), shortHelp='Change MAC Address')
        tbtn_alias = self.toolbar.AddTool(-1, '', icons.alias_32.GetBitmap(), shortHelp='Give an alias')
        self.toolbar.AddSeparator()
        tbtn_exit = self.toolbar.AddTool(-1, '', icons.exit_32.GetBitmap(), shortHelp='Exit')

        self.Bind(wx.EVT_TOOL, self.on_refresh, tbtn_refresh)
        self.Bind(wx.EVT_TOOL, self.on_cut, tbtn_cut)
        self.Bind(wx.EVT_TOOL, self.on_resume, tbtn_resume)
        self.Bind(wx.EVT_TOOL, self.on_change_mac, tbtn_change_mac)
        self.Bind(wx.EVT_TOOL, self.on_give_alias, tbtn_alias)
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
        self.unprotect()
        self.aliases.close()
        self.Close()

    def on_refresh(self, event):
        self.trigger_thread()

    def on_change_mac(self, event):
        res = requests.get('http://127.0.0.1:8013/change-mac/{}'.format(self._gw['iface']))
        if res.status_code == 200:
            if res.json()['result']['status'] == 'success':
                print('MAC Address changed')
            elif  res.json()['result']['status'] == 'failed':
                print('Couldn\'t change MAC')

    def on_give_alias(self, event):
        row = self.hosts_view.GetSelectedRow()
        if row == wx.NOT_FOUND:
            self.show_dialog('error', 'No Computer selected', 'Please select a computer from the list')
        else:
            mac = self.hosts_view.GetTextValue(row, 2)
            dialog = wx.TextEntryDialog(None,
                        'Enter an alias for the computer with MAC "{}" !'.format(mac),
                        'Text Entry', 'My Computer', style=wx.OK|wx.CANCEL)
            if dialog.ShowModal() == wx.ID_OK:
                alias = dialog.GetValue()
                self.aliases[mac] = alias
                self.trigger_thread()
            dialog.Destroy()

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
            try:
                alias = self.aliases[host['mac']]
            except KeyError:
                alias = ''
            self.hosts_view.AppendItem([
                host_icon,
                host['ip'],
                host['mac'],
                host['hostname'],
                alias
            ])

        self.PushStatusText('Ready')

    def is_server(self):
        try:
            res = requests.get('http://127.0.0.1:8013/status')
            if res.status_code == 200 and res.json()['status'] == 'success':
                return True
        except:
            logger.error(sys.exc_info()[1], exc_info=True)

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
            logger.error(sys.exc_info()[1], exc_info=True)

    def get_my(self, iface):
        try:
            res = requests.get('http://127.0.0.1:8013/my/{}'.format(iface))

            if res.status_code == 200 and res.json()['status'] == 'success':
                self._my = res.json()['my']

            elif res.status_code == 200 and res.json()['status'] == 'error':
                self.show_dialog('error', 'Error', res.json()['msg'])
                self.Close()
        except Exception as e:
            logger.error(sys.exc_info()[1], exc_info=True)

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
            logger.error(sys.exc_info()[1], exc_info=True)


    def unprotect(self):
        """
        Disable Protection Mode
        """
        try:
            res = requests.get('http://127.0.0.1:8013/unprotect')
            if res.status_code == 200 and res.json()['status'] == 'success':
                self.PushStatusText('Protection Disabled')
        except Exception as e:
            logger.error(sys.exc_info()[1], exc_info=True)

    def show_dialog(self, code, title, msg):
        if code == 'error':
            icon = wx.ICON_ERROR
        dlg = wx.MessageDialog(None, msg, title, wx.OK | icon)
        dlg.ShowModal()
        dlg.Destroy()
