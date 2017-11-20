import sys
import datetime as dt
import wx
from main_frame import MainFrameView
from setproctitle import setproctitle

setproctitle('tuxcut')

if __name__ == '__main__':
    app = wx.App(redirect=False)
    if dt.datetime.today().year == 2018:
        dlg = wx.MessageDialog(None, 'This is a BETA version,\nfor the latest stable version visit:\n\nhttp://a-atalla.github.io/tuxcut', 'This version of tuxcut is expired',
                               wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
        sys.exit()
    frame = MainFrameView(None)
    frame.Show()
    app.MainLoop()
