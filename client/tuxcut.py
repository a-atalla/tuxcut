import wx
from main_frame import MainFrameView
from setproctitle import setproctitle

setproctitle('tuxcut')

if __name__ == '__main__':
    app = wx.App(redirect=False)
    frame = MainFrameView(None)
    frame.Show()
    app.MainLoop()
